# Hallucination Mitigation

> **Type:** Study notes

## Why interviewers ask this

"How do you prevent hallucination" is a near-universal question at AI companies, and the weak
answer is "prompt it to not make things up." Interviewers want to hear this framed as **engineering
constraints that reduce the surface area for hallucination**, not a prompting trick that solves it —
because it doesn't fully solve it, and pretending otherwise is itself a red flag.

## What hallucination actually is, structurally

An LLM generates the statistically most plausible next tokens given its training and the prompt —
it has no built-in mechanism to distinguish "this is something I actually retrieved/verified" from
"this is a plausible-sounding continuation." A hallucination isn't the model "lying" — it's the
model doing exactly what it does (predict plausible text) in a case where plausible and true
diverge. This framing matters in an interview: it explains *why* no prompt wording alone eliminates
it, and points toward the actual mitigations (below), which all work by constraining what the model
can say or by verifying what it did say — not by asking it more firmly to be accurate.

## Grounding — give the model the facts instead of relying on its memory

The single highest-leverage mitigation: **retrieve the actual facts and put them in context**
(this is RAG's core value proposition — see [RAG System Architecture](02_rag_system_architecture.md))
instead of asking the model to recall facts from training. A model answering from provided context
is far less likely to fabricate than one answering from parametric memory, especially for anything
specific, recent, or domain-internal (your company's own data, which was never in training data at
all).

```python
system = (
    "Answer the user's question using ONLY the information in the context below. "
    "If the context does not contain enough information to answer, respond exactly: "
    "\"I don't have enough information to answer that.\" Do not use outside knowledge."
)
```

Explicitly instructing refusal-on-insufficient-context, and giving the model an exact phrase to use,
measurably reduces confident fabrication compared to an open-ended "be accurate" instruction — the
model has a concrete, easy-to-produce escape hatch instead of being implicitly pressured to produce
*some* answer.

## Citations — make claims traceable, and verify them

Requiring the model to cite which source chunk supports each claim (see the numbered-context pattern
in [RAG System Architecture](02_rag_system_architecture.md)) does two things: it nudges generation
toward grounded claims (the model is more likely to stay faithful to context when explicitly asked
to attribute), and — more importantly — it makes claims **programmatically checkable**. You can
verify a citation actually exists and roughly supports the sentence it's attached to (even a cheap
check like "does the cited chunk contain overlapping key terms with the claim" catches a real class
of ungrounded claims) before showing the answer to a user, or flag low-confidence answers for review.

## Structured constraints reduce the fabrication surface

The freer the output format, the more room for invented detail. Where the task allows it, constrain
output structurally:
- Classification into a fixed enum instead of free-text categorization — there's no way to
  "hallucinate" a category outside the enum if you validate against it (see
  [Prompt Engineering Fundamentals](03_prompt_engineering_fundamentals.md)).
- Extraction with a schema that only pulls fields that exist in the source, with explicit `null`
  allowed rather than forcing the model to fill every field.
- For anything numeric/factual and independently verifiable (a price, a date, a status), prefer
  fetching it directly from your database over asking the model to state it from context, even if
  it saw the number in the retrieved context — deterministic lookups don't hallucinate.

## Confidence signals — when to say "I'm not sure"

Providers vary in native confidence signaling (some expose token-level log probabilities), but even
without that, you can build cheap proxies:
- **Self-consistency check** — generate the answer twice (or with two slightly different retrieval
  sets) and flag disagreement as low-confidence, since a well-grounded answer should be stable.
- **Retrieval-score threshold** — if the top retrieved chunk's similarity score is below a threshold,
  the system likely doesn't have good grounding for this query at all; short-circuit to "I don't have
  information on that" before even calling the LLM, rather than letting a weak-grounding case
  through to generation.
- **Explicit judge pass** — a second, cheaper LLM call that specifically checks "is every claim in
  this answer supported by the provided context," used selectively (not on every request, given the
  added cost/latency) for high-stakes answers.

## What mitigation does NOT mean: "the LLM double-checks itself and it's now safe"

A common interview trap is treating "ask the model to verify its own answer" as a solved problem —
it helps somewhat (catching some errors) but the same model making the same kind of mistake is not
a reliable check on itself; it can just as easily hallucinate a confident-sounding verification.
State clearly: for anything with real consequences (financial, legal, medical, irreversible
actions), hallucination mitigation reduces but does not eliminate risk, and a human-in-the-loop or a
deterministic guard (see [Guardrails & Content Safety](08_guardrails_and_content_safety.md)) is
still required at the boundary where the model's output causes a real-world effect.

## Interview questions

**Q: A user asks your RAG-based support bot a question outside your product's documentation. What
should happen?**
The retrieval step should surface low-similarity/no-match results; the system prompt should
instruct explicit refusal on insufficient context (with the exact-phrase pattern above), and ideally
a similarity-score threshold short-circuits to the refusal *before* the LLM call — cheaper and more
reliably correct than hoping the model refuses gracefully on its own.

**Q: Your hallucination mitigations reduced but didn't eliminate the problem — how do you decide
whether that residual rate is acceptable to ship?**
Depends entirely on the consequence of a wrong answer: a wrong answer in an internal
documentation-search tool with a human reading it is low-stakes; a wrong answer that triggers an
automated refund or medical/legal guidance is not. Match the mitigation investment (and whether a
human-in-the-loop gate is mandatory before any consequential action) to the actual blast radius of
being wrong, not a single global "is X% hallucination rate okay."

**Q: How would you measure hallucination rate for a shipped feature, not just guess at it?**
Build (or borrow) an eval set with known-correct answers (see
[Model Evaluation](06_model_evaluation.md)), score generated answers against it (exact match where
possible, LLM-as-judge fact-checking against source context otherwise), and track this as an
ongoing production metric via sampled review of live traffic, not a one-time check at launch.

## Exercise

Build a small RAG system over 5 documents (reuse the one from
[RAG System Architecture](02_rag_system_architecture.md) if you built it), then ask it 5 questions
the documents don't answer. Without a refusal instruction, observe how often it fabricates a
plausible-sounding answer anyway; add the explicit refusal-with-exact-phrase instruction and
similarity-threshold short-circuit, and re-measure.
