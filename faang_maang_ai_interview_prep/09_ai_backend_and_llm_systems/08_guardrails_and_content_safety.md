# Guardrails & Content Safety

> **Type:** Study notes

## Why interviewers ask this

Any product exposing a raw or near-raw LLM to end users inherits new failure/abuse surfaces: users
who try to make it say something harmful/off-brand, users who try to jailbreak it into ignoring
your rules, and legitimate users who get a bad experience from unfiltered output. Interviewers want
to see a **layered** approach (defense in depth), not a single "add a moderation check" answer.

## Input guardrails vs. output guardrails

- **Input guardrails** — checks on what the user sends *before* it reaches the LLM: moderation
  classifiers for clearly abusive/harmful requests, prompt-injection pattern detection, basic scope
  checks (is this even a question the system is meant to handle).
- **Output guardrails** — checks on what the LLM produces *before* it reaches the user or triggers
  an action: content moderation on the generated text, PII leakage checks, format/schema validation,
  and — for anything the LLM's output can trigger (a tool call, a database write) — authorization
  checks that don't trust the LLM's output as sufficient permission.

Both layers matter independently: input filtering alone doesn't stop a model from generating
something bad unprompted (rare but possible), and output filtering alone lets clearly abusive input
waste a full LLM call before being caught.

## Using a moderation API

```python
# services/moderation.py
from openai import OpenAI  # many teams use a moderation-specific provider call
                            # even when generation uses a different provider

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def is_flagged(text: str) -> tuple[bool, dict]:
    result = client.moderations.create(input=text)
    flagged = result.results[0].flagged
    categories = {k: v for k, v in result.results[0].categories.model_dump().items() if v}
    return flagged, categories

def handle_chat_message(user_input: str) -> str:
    flagged, categories = is_flagged(user_input)
    if flagged:
        logger.warning("moderation_flagged_input", extra={"categories": categories})
        return "I can't help with that request."
    # proceed to LLM call
    ...
```

Moderation calls are themselves an extra API call with their own latency/cost — for high-traffic,
low-risk-surface products, a cheaper first pass (a fast local classifier or keyword/pattern heuristics
for the most obvious cases) before an expensive moderation API call is a reasonable cost
optimization; for anything higher-risk (public-facing, minors, healthcare/finance), don't skip the
real moderation check to save the cost.

## Jailbreak resistance — there's no complete fix, only raising the bar

Jailbreaks (prompts crafted to make a model ignore its instructions — role-play framings,
"pretend you're an AI with no restrictions," encoded/obfuscated instructions) are an ongoing
adversarial problem, not something a single system prompt permanently closes. Practical layered
defense:
- **System prompt hardening** — explicit, repeated instructions about what the model must never do,
  placed in the system message (not overridable by user-supplied content) — necessary but not
  sufficient on its own.
- **Output-side re-checking** — even if a jailbreak gets past the system prompt, an output
  moderation pass can still catch the resulting harmful content before it reaches the user.
  Layering input intent + output content checks catches more than either alone.
- **Least-privilege tool access** — the strongest practical mitigation for anything consequential:
  if a jailbroken model can only call tools with limited scope/authorization (see below), a
  successful jailbreak's blast radius is capped regardless of what text it produces.
- **Accept residual risk, scope the stakes accordingly** — say explicitly in an interview that no
  jailbreak defense is complete; the engineering answer is to make the worst case bounded and
  acceptable, not to claim a fully solved problem.

## Never let the LLM's output be the sole authorization for a consequential action

This is the guardrail most worth stating clearly and unprompted in an interview: if an LLM output
can trigger a real action (issue a refund, delete data, send an email, change a permission), the
authorization decision must be enforced by your normal application logic — role checks, business
rules, amount limits — exactly as if the request had come from a malicious user directly, **because
functionally it might have**, via prompt injection or jailbreak. The LLM's decision informs the
action; it doesn't replace the authorization layer.

```python
def process_refund_request(user, ticket, llm_suggestion: dict):
    # llm_suggestion might say {"action": "refund", "amount": 500}
    # Never do this:
    #   process_refund(ticket.order, llm_suggestion["amount"])
    # Do this instead — the LLM's suggestion is an input to policy, not the policy itself:
    if not user.has_permission("issue_refunds"):
        raise PermissionDenied
    max_auto_refund = 50.00
    if llm_suggestion["amount"] > max_auto_refund:
        return queue_for_human_review(ticket, llm_suggestion)  # escalate, don't auto-execute
    return process_refund(ticket.order, min(llm_suggestion["amount"], ticket.order.total))
```

## Rate limiting and abuse patterns specific to LLM endpoints

Beyond standard API rate limiting (see
[Rate Limiting](../05_backend_engineering/05_rate_limiting.md)), LLM endpoints have an abuse pattern
that's expensive in a way most endpoints aren't: a single abusive user can run up real API cost by
sending many long-context requests. Per-user token-based rate limiting (not just request-count
limiting) is worth calling out as the LLM-specific extension of standard rate limiting — see
[Cost, Latency, Throughput](13_cost_latency_throughput_batching_caching.md).

## Interview questions

**Q: A user finds a jailbreak that gets your customer-support bot to say something off-brand. How
do you respond, both immediately and structurally?**
Immediately: this is a content-safety incident — log it, if the output guardrail should have caught
it, treat that as a bug (missing output-side check, not just a prompt-wording gap). Structurally:
this confirms system-prompt-only defense is insufficient — add or tighten the output moderation
pass, and re-evaluate whether this bot has any tool access that a jailbreak could abuse beyond just
embarrassing text.

**Q: How would you design guardrails for an internal tool (used only by trusted employees) vs. a
public-facing chatbot?**
Internal/trusted-user tools can reasonably run lighter guardrails (fewer input restrictions, since
the threat model is narrower) but should NOT skip output-side authorization checks on consequential
actions — an internal user's LLM-assisted action can still be a mistake (not malice) that a
guardrail should catch. Public-facing surfaces need the full layered stack: input moderation, output
moderation, jailbreak-hardened prompts, and strict tool-call authorization, since the threat model
includes deliberate adversarial users at scale.

**Q: Where's the line between a guardrail and just… good input validation?**
There isn't a hard line — a guardrail is input/output validation adapted for the fact that the
"input" and "output" are natural language rather than structured data, so the validation methods
differ (moderation classifiers, pattern/heuristic checks, LLM-as-judge) but the engineering
principle (validate at the boundary, don't trust unvalidated data to drive consequential behavior)
is identical to any other system boundary.

## Exercise

Add a moderation check (real API or a simple keyword-based stand-in if you don't want to call a
paid API) to the RAG Q&A loop from earlier exercises. Test it against a few clearly-fine inputs and
a few flagged-category inputs, and verify the flagged ones are rejected before an LLM call is made
at all (check this via logging — confirm the LLM API was never actually invoked for the rejected
case).
