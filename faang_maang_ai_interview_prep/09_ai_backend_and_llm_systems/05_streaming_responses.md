# Streaming Responses

> **Type:** Study notes

## Why interviewers ask this

Chat-style LLM UIs stream tokens because a 5-10 second silent wait feels broken while the same
latency spread across visible incremental output feels fast. Interviewers use this topic to check
whether you can implement streaming correctly at the HTTP layer (SSE, chunked responses), handle a
mid-stream failure gracefully, and reason about backpressure — not just call a provider's `stream=True`
flag and assume the rest is free.

## Server-Sent Events (SSE) — the standard mechanism

SSE is a simple, one-directional (server → client), HTTP-native streaming protocol — the client
opens a normal HTTP connection and the server keeps writing `data: ...\n\n` chunks over it. It's the
right fit for LLM token streaming because it's simpler than WebSockets (no bidirectional handshake
needed for this use case) and works through most proxies/load balancers without special config,
unlike raw chunked encoding in some setups.

```python
# views.py — Django, using StreamingHttpResponse
import json
from django.http import StreamingHttpResponse
from .llm_client import stream_completion

def chat_stream_view(request):
    user_message = request.POST["message"]

    def event_stream():
        try:
            for chunk in stream_completion(system=SYSTEM_PROMPT, user=user_message):
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # tell nginx not to buffer the stream
    return response
```

`X-Accel-Buffering: no` matters in production behind nginx — without it, nginx buffers the whole
response before sending it to the client, which silently defeats streaming even though the code
above is correct. This is a real, commonly-hit gotcha worth naming unprompted.

## The provider side — consuming a streamed completion

```python
def stream_completion(system: str, user: str):
    with anthropic_client.messages.stream(
        model="claude-sonnet-4-5", max_tokens=1024,
        system=system, messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            yield text
```

The provider SDK gives you an iterator of incremental text deltas; your job is just to relay them to
the client as they arrive rather than buffering the full response server-side and sending it at
once (which would defeat the entire point).

## WebSockets vs. SSE — when WebSockets actually earn their complexity

SSE is sufficient and simpler whenever the pattern is "client sends one request, server streams one
response back." Reach for WebSockets (Django Channels in this stack) only when you need **true
bidirectional** communication in the same connection — the client needs to send follow-up
messages, cancel a generation, or receive out-of-band events (another user joined the chat) while a
response is still streaming. Don't default to WebSockets for simple one-shot streaming chat — it's
more infrastructure (a different server model, connection state to manage) for capability most
single-turn streaming features don't need.

## Handling mid-stream failure

A stream can fail after already sending partial output — the client has half an answer, then the
connection breaks or the provider errors out mid-generation. Handle this explicitly, don't let it
manifest as a silently truncated response:
- Send a distinguishable terminal event on error (`{"error": "..."}` before `[DONE]`, as in the
  view above) so the client can show "generation interrupted" instead of silently rendering a
  truncated answer as if it were complete.
- Decide, per use case, whether a partial answer should be persisted (e.g. saved to chat history) —
  usually yes, marked as incomplete, rather than discarded, since regenerating from scratch wastes
  the tokens already generated and the user's wait time.
- If retrying, retry the *whole* generation, not "continue from where it broke" — LLM completions
  aren't naturally resumable mid-generation without re-sending full context, and naively splicing a
  retry's output onto a partial one risks incoherent output.

## Backpressure — the client is usually the slow one, not the LLM

In practice, the LLM's token-generation rate is the bottleneck (tens of tokens/sec), not the
client's ability to receive them — real backpressure problems in this pipeline are rarer than in,
say, a high-throughput data pipeline. The place it does matter: if you're relaying a stream to
**multiple** consumers (e.g. fanning one generation out to a UI and a logging pipeline
simultaneously), a slow consumer (a logging sink under load) shouldn't block or slow down the fast
one (the UI) — decouple with a queue rather than writing to both synchronously in the same loop.

## Interview questions

**Q: Why does streaming reduce perceived latency without actually reducing total generation time?**
Because time-to-first-token (TTFT) is what the user experiences as "responsiveness" — streaming
surfaces the first tokens in a few hundred milliseconds to ~1s instead of making the user wait for
the entire response (which might take 5-10s for a long answer) before seeing anything. Total wall-clock
time to the last token is roughly the same either way; UX is about when output *starts* appearing.

**Q: Your streaming endpoint works locally but silently doesn't stream in production behind nginx —
what's the likely cause?**
nginx buffering the proxied response by default — fixed with `X-Accel-Buffering: no` on the response
(or `proxy_buffering off` in nginx config for that location). This is the single most common
real-world streaming gotcha and a strong signal of hands-on experience if you name it unprompted.

**Q: How would you let a user cancel an in-progress generation?**
Client-side: close the SSE connection (abort the fetch/EventSource) — Django's
`StreamingHttpResponse` generator will raise on write once the client disconnects, so wrap the
provider stream loop to catch that and break cleanly, and (if the provider SDK supports it) call its
cancel/abort so you stop being billed for tokens generated after the user walked away.

## Exercise

Implement the SSE view above against a real provider's streaming API, then simulate a mid-stream
client disconnect (close the browser tab or `curl` connection partway through) and verify server-side
that generation stops promptly rather than continuing to completion in the background wastefully.
