# Model Evaluation

> **Type:** Study notes

## Why interviewers ask this

"How do you know your LLM feature actually works, and keeps working after you change the prompt or
swap models?" is a question that exposes candidates who've only ever eyeballed a few outputs in a
playground. Interviewers want engineering rigor applied to a non-deterministic system: a real eval
set, a repeatable scoring method, and regression testing — the same instincts as testing any other
part of the system, adapted for outputs that don't have a single "correct" string.

## Why you can't just unit-test LLM output with `assertEqual`

LLM output is non-deterministic (even at low/zero temperature, in practice) and there's often no
single correct string — "summarize this article" has many valid summaries. Evaluation needs
different tools than exact-match assertions:

- **Exact/structural match** — still works for constrained tasks: does the output parse as valid
  JSON matching a schema, does a classification land in the correct category, does an extracted
  field match the expected value. Use this wherever the task is constrained enough to support it —
  it's cheap, fast, and deterministic.
- **Reference-based similarity** — compare generated text to a reference answer via embedding
  similarity or ROUGE/BLEU-style overlap when some semantic flexibility is expected but you still
  have a "gold" answer to compare against.
- **LLM-as-judge** — use a (usually stronger or same-tier) LLM to score the output against a rubric
  when there's no single correct answer (open-ended generation, summarization quality, tone).
- **Human review** — the ground truth for calibrating the above, and still necessary periodically
  even once automated eval is in place, since LLM-as-judge itself can drift or share blind spots
  with the model it's judging.

## Building an offline eval set

```python
# evals/ticket_classifier_eval.py
EVAL_SET = [
    {"input": "My package never arrived and it's been 3 weeks", "expected_category": "shipping", "expected_urgency": "high"},
    {"input": "Just wondering if you ship to Canada", "expected_category": "shipping", "expected_urgency": "low"},
    {"input": "Charged twice for the same order!!", "expected_category": "billing", "expected_urgency": "high"},
    # ... 30-100 real, representative examples, including known-hard edge cases
]

def run_eval(classifier_fn) -> dict:
    results = [classifier_fn(case["input"]) for case in EVAL_SET]
    category_acc = sum(
        r["category"] == c["expected_category"] for r, c in zip(results, EVAL_SET)
    ) / len(EVAL_SET)
    urgency_acc = sum(
        r["urgency"] == c["expected_urgency"] for r, c in zip(results, EVAL_SET)
    ) / len(EVAL_SET)
    return {"category_accuracy": category_acc, "urgency_accuracy": urgency_acc, "n": len(EVAL_SET)}
```

**What makes a good eval set**: real examples pulled from actual production inputs (or realistic
synthetic ones), deliberately including known-hard cases and edge cases, not just easy majority-case
examples — an eval set of only easy cases gives false confidence. Keep it version-controlled next to
the code, exactly like a test fixture, so eval-set changes are reviewable.

## LLM-as-judge — how to do it without fooling yourself

```python
JUDGE_PROMPT = """You are evaluating an AI assistant's summary against the source article.
Score 1-5 on: (1) factual accuracy — does it contain anything not supported by the article,
(2) coverage — does it capture the article's key points.
Article: {article}
Summary: {summary}
Respond with JSON: {{"accuracy": int, "coverage": int, "reasoning": str}}"""
```

Pitfalls to watch for (and to name in an interview — this is where LLM-as-judge answers separate
strong from shallow):
- **Self-preference bias** — a model tends to rate its own outputs (or outputs in its own style)
  more favorably; where possible, use a different/stronger model as judge than the one being
  evaluated.
- **Position bias** — when comparing two outputs side by side, judges can favor whichever is
  presented first; randomize order across eval runs.
- **The judge needs its own sanity-checking** — periodically spot-check judge scores against human
  ratings on a sample; if they diverge, the judge prompt (or the judge model) is the thing that's
  broken, not necessarily the system under test.

## Regression testing prompts and model versions

Treat both prompt changes and model upgrades (a provider deprecates a model version, or you swap to
a cheaper one) as **changes requiring the eval suite to pass**, exactly like a code change requiring
CI to pass:

```python
# In CI, or run manually before a prompt/model change ships
def test_no_regression():
    baseline = load_baseline_scores()  # committed alongside the eval set
    current = run_eval(classifier_fn)
    assert current["category_accuracy"] >= baseline["category_accuracy"] - 0.02, (
        f"Category accuracy regressed: {current['category_accuracy']} vs baseline {baseline['category_accuracy']}"
    )
```

A small tolerance band (here, 2 percentage points) accounts for the model's inherent
non-determinism — don't require bit-for-bit reproducibility, but do require the eval suite to catch
a real regression (a prompt tweak that quietly breaks 15% of cases) before it reaches production.

## Online evaluation — after it ships

Offline eval sets can't cover every real input distribution; pair them with production signals:
- **Implicit feedback** — thumbs up/down, whether a user edited/discarded a generated draft, whether
  a suggested reply was sent as-is or heavily modified.
- **A/B testing prompt or model versions** — same statistical discipline as any other product
  experiment (see [Prompt Engineering Fundamentals](03_prompt_engineering_fundamentals.md)), with a
  concrete success metric defined before the test starts, not chosen post-hoc from whatever looks
  favorable.
- **Sampled human review of live traffic** — a small ongoing sample of real production outputs
  reviewed periodically catches drift an offline eval set (frozen at creation time) won't.

## Interview questions

**Q: How do you evaluate an open-ended task like "write a product description" where there's no
single correct answer?**
Define a rubric (accuracy to product facts, tone match, length compliance, no fabricated claims)
and use LLM-as-judge scored against that rubric, calibrated periodically against human ratings on a
sample. Pair with hard constraints checked structurally (character limit, required fields present)
rather than trying to make the judge responsible for everything.

**Q: You want to switch from GPT-4-class to a cheaper model for a classification task to cut costs.
How do you decide if that's safe?**
Run the existing eval set against the cheaper model, compare accuracy against the current baseline
with a defined acceptable tolerance, and if it's close, do a canary rollout on a small percentage of
real traffic with online monitoring (implicit feedback signals) before a full cutover — the same
methodology as any risky infra migration, not something specific to LLMs.

**Q: What's the risk of only ever testing your LLM feature manually in a playground?**
No repeatability (can't tell if a prompt change actually improved things or you got a lucky sample),
no regression detection (a later change can silently break something you tested once and never
re-checked), and no coverage of edge cases you didn't happen to think to try manually — exactly the
argument for automated tests over manual QA in traditional software, applied here.

## Exercise

Build a 20-example eval set for a text classification task (pick any — sentiment, spam/not-spam,
support-ticket routing), implement exact-match scoring, then deliberately introduce a prompt change
that you expect to hurt one category's accuracy and confirm the eval set catches the regression.
