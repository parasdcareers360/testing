# Fine-Tuning vs. RAG Trade-offs

> **Type:** Study notes

## Why interviewers ask this

"Should we fine-tune or use RAG" is a genuinely common product/engineering decision, and a lot of
candidates reach for fine-tuning first because it sounds more sophisticated — when in most real
cases RAG is the right (cheaper, faster-to-iterate, more maintainable) answer. Interviewers use this
to see if you understand what each technique actually changes about the model's behavior, because
they solve **different problems**, not competing solutions to the same problem.

## What each one actually changes

- **RAG** gives the model access to **facts/knowledge it doesn't have** by retrieving and inserting
  relevant information into the prompt at query time. The model's underlying behavior, style, and
  reasoning ability are unchanged — you're changing what it *knows* for this specific call, not how
  it behaves in general.
- **Fine-tuning** changes the model's **weights** via additional training on examples, which changes
  how the model *behaves* — its tone, output format adherence, domain-specific reasoning patterns, or
  task-specific skill — persistently, without needing to be told in every prompt.

The framing worth stating directly in an interview: **RAG is for knowledge, fine-tuning is for
behavior.** A model that doesn't know your company's return policy needs RAG (retrieve the policy
document). A model that keeps writing responses in the wrong tone/format despite explicit prompt
instructions, or needs to reliably do a narrow specialized task better than prompting alone achieves,
is a fine-tuning candidate.

## When RAG is the right tool

- Knowledge changes frequently (product catalog, pricing, documentation) — RAG's knowledge source
  updates by updating the retrieval corpus; no retraining needed, changes are live immediately.
- You need traceability/citations — RAG can point to which source document supported an answer;
  fine-tuned knowledge is baked into weights with no way to cite where a specific fact came from.
- The knowledge is large or per-tenant — fine-tuning a separate model per customer/tenant doesn't
  scale operationally; a shared model with tenant-scoped retrieval does.
- You want to reduce hallucination on facts — see
  [Hallucination Mitigation](07_hallucination_mitigation.md); grounding in retrieved context is a
  stronger anti-hallucination lever than fine-tuning, which can still confidently misstate facts it
  was trained on if training data was incomplete or the question falls outside it.

## When fine-tuning is the right tool

- **Consistent output format/style that prompting alone won't reliably hold** across many varied
  inputs — e.g. always producing a very specific structured format under adversarial/edge-case
  inputs where few-shot prompting occasionally still drifts.
- **Domain-specific task performance** where the base model's general training doesn't cover the
  task well enough even with good prompting and examples — e.g. classifying highly specialized
  internal jargon/categories that don't resemble anything in general training data, where few-shot
  examples in the prompt aren't enough signal.
- **Reducing prompt length/cost at scale** — if achieving acceptable quality currently requires a
  large few-shot prompt on every call, fine-tuning on those same examples can bake the pattern into
  the model, shrinking the prompt (and therefore per-call cost) needed to get comparable behavior.
- **Latency-sensitive tasks where a smaller fine-tuned model can match a larger general model's
  quality** on the narrow task — a small model fine-tuned for one specific job can sometimes
  outperform a much larger general model on that job specifically, at a fraction of the cost/latency.

## What fine-tuning does NOT fix

- **It does not reliably reduce hallucination on facts** — a fine-tuned model can still confidently
  state something wrong if the underlying knowledge wasn't in its training data or training
  examples; fine-tuning shapes behavior/style, it doesn't give the model a lookup mechanism for facts
  the way retrieval does.
- **It's not a good fit for frequently-changing information** — every knowledge update means
  re-fine-tuning and redeploying a new model version, which is slow and costly compared to updating
  a retrieval corpus.
- **It doesn't solve prompt injection or safety issues** on its own — those are still handled at the
  guardrail/authorization layer (see [Guardrails & Content Safety](08_guardrails_and_content_safety.md)),
  regardless of whether the underlying model is fine-tuned.

## Operational cost comparison — the part candidates often underweight

| | RAG | Fine-tuning |
|---|---|---|
| Iteration speed | Update the corpus, changes are live immediately | Requires a new training run + evaluation + redeployment per change |
| Cost to change | Cheap (re-embed/re-index changed documents) | Expensive (compute cost of a training run, plus eval before shipping the new weights) |
| Infra needed | Vector store + retrieval pipeline (this candidate's existing stack: pgvector, Celery) | Training pipeline, dataset curation/versioning, model hosting for the resulting custom weights (or a provider's fine-tuning API) |
| Risk of regression | Lower — bad new document additions are easy to remove/roll back | Higher — a fine-tuning run can degrade general capability if not carefully evaluated (**catastrophic forgetting** — the model can lose some general skill while gaining the fine-tuned one, especially with a small or narrow training set) |

## Combining both — the common real-world pattern

The two aren't mutually exclusive: fine-tune a model to reliably follow your desired output
format/tone/task behavior, **and** use RAG to feed it current, factual, traceable knowledge at query
time. A support-bot example: fine-tune for your company's specific tone and the exact structured
response format your UI expects, while RAG supplies the actual up-to-date policy/product information
that answers vary on. Neither alone is the complete answer for a sophisticated production system;
each is solving a different half of the problem.

## Interview questions

**Q: A team wants to fine-tune a model on their product documentation so it "knows the product."
What would you push back on?**
That's a RAG problem, not a fine-tuning problem — documentation is exactly the kind of frequently-
changing, needs-citation, large-corpus knowledge RAG handles well and fine-tuning handles poorly
(stale the moment docs update, no traceability, expensive to refresh). Ask what specific *behavior*
(not knowledge) they're actually trying to change before agreeing fine-tuning is the right tool.

**Q: When would fine-tuning actually outperform prompting + RAG for a task?**
When the task needs a narrow, well-defined behavior pattern that few-shot prompting achieves
inconsistently across edge cases (format that must never drift, however the input varies), or when
per-call cost/latency matters enough that shrinking a large few-shot prompt into fine-tuned model
behavior is worth the fixed cost of training — both are behavior/format problems, not knowledge
problems, which is the tell that fine-tuning is the right lever.

**Q: What's "catastrophic forgetting" and why does it matter when evaluating whether to fine-tune?**
Fine-tuning on a narrow dataset can degrade the model's performance on capabilities outside that
narrow training distribution — a model fine-tuned hard on customer-support-ticket classification
might get measurably worse at general reasoning or unrelated tasks it still needs to do. This is why
a fine-tuning decision needs a broader eval suite (not just the target task's eval set) before
shipping the resulting model — see [Model Evaluation](06_model_evaluation.md).

## Exercise

Take a real feature idea (e.g. "an assistant that answers questions about internal engineering
runbooks") and write a one-paragraph justification for whether it needs RAG, fine-tuning, both, or
neither — explicitly naming which specific requirement (knowledge freshness, format consistency,
cost at scale, traceability) drives the choice, not a generic "RAG is usually better" answer.
