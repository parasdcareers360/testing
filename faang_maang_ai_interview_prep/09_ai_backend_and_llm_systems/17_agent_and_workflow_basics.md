# Agent & Workflow Basics

> **Type:** Study notes

## Why interviewers ask this

"Agent" is one of the most overloaded, hyped words in this space right now — interviewers use this
topic to separate candidates who can precisely define what an agent actually is (a loop where the
model chooses actions/tools, and the result feeds back into the next decision) from those using it
as a buzzword. Just as important: knowing **when a fixed pipeline is the better engineering choice**
than an agent, which is the more senior-signaling half of this topic.

## Tool calling — the mechanism underneath every agent

Before "agent," there's tool/function calling: the model is given a set of available functions (name,
description, parameter schema) and, instead of only generating text, can output a structured request
to call one of them — your application code executes the actual function and returns the result to
the model as part of the ongoing conversation.

```python
tools = [
    {
        "name": "search_orders",
        "description": "Search a customer's orders by status",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
                "status": {"type": "string", "enum": ["pending", "shipped", "delivered", "cancelled"]},
            },
            "required": ["customer_id"],
        },
    },
]

def handle_tool_call(tool_name: str, tool_input: dict, user) -> dict:
    if tool_name == "search_orders":
        # Authorization check — never trust the model's tool call as sufficient permission
        if tool_input["customer_id"] != user.customer_id and not user.is_staff:
            raise PermissionDenied
        orders = Order.objects.filter(
            customer_id=tool_input["customer_id"], status=tool_input.get("status")
        )
        return {"orders": [o.to_dict() for o in orders]}
    raise ValueError(f"Unknown tool: {tool_name}")
```

The model decides *when* and *with what arguments* to call a tool based on the conversation; your
code is responsible for actually executing it and for **authorization on every call**, exactly as
noted in [Guardrails & Content Safety](08_guardrails_and_content_safety.md) — the model choosing to
call `search_orders(customer_id=99)` is not itself permission to return customer 99's data to the
current user.

## An agent loop, concretely

An "agent" is what you get when you put tool calling in a loop: the model can call a tool, see the
result, decide to call another tool based on that result, and continue until it decides the task is
done — as opposed to a single request → single tool call → single response.

```python
def run_agent(user_query: str, user, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": user_query}]
    for step in range(max_steps):
        response = llm_client.messages.create(
            model="claude-sonnet-4-5", tools=tools, messages=messages,
        )
        if response.stop_reason != "tool_use":
            return response.content[0].text  # model produced a final answer, loop ends

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = handle_tool_call(block.name, block.input, user)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(result)})
        messages.append({"role": "user", "content": tool_results})

    return "I wasn't able to complete this within the allowed steps."  # bounded, not infinite
```

`max_steps` is not optional — an unbounded agent loop is a real production hazard (runaway cost from
repeated tool calls, or a genuinely infinite loop if the model gets stuck retrying a failing
approach). Always cap steps and log/alert when a run hits the cap, since that's a signal the task or
tool design needs work.

## Fixed pipeline vs. agent — the decision that actually matters

| | Fixed pipeline (predetermined sequence of steps) | Agent (model decides the sequence dynamically) |
|---|---|---|
| When the steps needed are known in advance | Ideal — encode them directly, e.g. the RAG pipeline (embed → retrieve → generate) is a fixed pipeline, not an agent, even though it "uses AI" | Overkill — you're paying agent-loop latency/cost/complexity for a sequence you could have just written in code |
| When the right steps depend on the specific query and can't be predetermined | Awkward — you'd need to hand-code every branch | This is the actual case for an agent: "figure out which of these 5 tools are needed and in what order, based on what this specific request needs" |
| Predictability/debuggability | High — same steps every time, easy to test and reason about | Lower — the model's chosen path can vary between similar-looking queries, harder to guarantee coverage of edge cases |
| Cost/latency | Bounded and known | Variable — depends on how many steps the model decides to take |
| Failure mode | A step fails, you know exactly which and why | The model can choose a poor tool sequence, loop unproductively, or stop early — failure modes are less predictable |

**The interview-ready framing**: don't reach for "agent" by default. If you can enumerate the steps
a task needs ahead of time, write a fixed pipeline — it's more predictable, cheaper, easier to test,
and easier to debug. Reach for an agent specifically when the *sequence itself* genuinely needs to be
decided per-request based on information you don't have until the request arrives (e.g. "answer this
support question, which might need looking up an order, checking a policy doc, or both, in an order
that depends on the question"). Most of what gets marketed as "agentic" in practice is closer to a
fixed pipeline with one or two decision points — know the difference and describe your own systems
accurately rather than over-claiming "agent" for marketing appeal.

## Multi-agent systems — mention, don't overclaim

Multi-agent setups (multiple LLM instances with different roles/tools coordinating, e.g. a
"planner" agent delegating to specialist "worker" agents) exist and are an active area of
development, but add real coordination complexity (state sharing, failure handling across agents,
significantly higher token cost from multiple models' worth of reasoning per task) that isn't
justified for most production use cases at this candidate's level. Know it exists and can be named,
but the honest, senior-signaling answer to "would you build a multi-agent system for X" is usually
"only after confirming a single agent (or a fixed pipeline) genuinely can't handle it" — not
reaching for it as a default architecture.

## Interview questions

**Q: What's the actual difference between a RAG pipeline and an "agent"?**
A RAG pipeline is a fixed sequence (embed → retrieve → generate) executed the same way every time —
no dynamic decision-making about *which* steps to take. An agent involves the model choosing, at
each step, what action (tool call) to take next based on the evolving conversation/results, in a
loop that continues until the model decides it's done. RAG uses an LLM; it isn't an agent unless the
model is also deciding the retrieval/tool strategy dynamically.

**Q: How do you prevent an agent from taking a harmful or unauthorized action via a tool call?**
Authorization checks in your tool-execution code, not in the prompt — the model choosing to call a
tool is a request, not a permission grant; your code must independently verify the calling user is
allowed to perform that action with those specific parameters, exactly as it would for a direct API
request. See [Guardrails & Content Safety](08_guardrails_and_content_safety.md).

**Q: An agent-based feature is unpredictable — it sometimes takes 2 steps, sometimes 8, for
similar-looking queries. Is that a bug?**
Not necessarily a bug, but it's a real cost/latency variance you need to plan for (budget for the
worst case, not the average, and cap steps) — and it's worth asking whether the task actually needs
agent-style dynamic decision-making or whether the variance suggests a fixed pipeline with one or two
conditional branches would give more predictable behavior for equivalent quality.

## Exercise

Implement the `run_agent` loop above with two simple tools (e.g. `get_weather(city)` and
`get_time(timezone)`, both returning canned/mocked data), ask it a question requiring both tools in
sequence, and trace how many steps it takes. Then modify one tool to return an error and observe how
the agent handles (or fails to handle) an unexpected tool failure mid-loop.
