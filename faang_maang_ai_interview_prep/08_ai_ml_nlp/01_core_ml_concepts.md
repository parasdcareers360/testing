# Core ML Concepts

> **Type:** Study notes

## Why interviewers ask this

For an AI-backend candidate, this is a filter question, not a deep-dive: it establishes whether
you can have a coherent conversation with the ML engineers you'll be building infrastructure for.
Interviewers are checking for correct mental models and vocabulary, not derivations — if you can
explain overfitting, the train/inference split, and what a loss function is doing in one clear
paragraph each, you've cleared the bar for a backend-track role.

## What a model actually is

A trained model is a function `f(x) → y` where the function's *parameters* (weights) were fit to
data rather than hand-written. "Training" is the process of searching for parameter values that
make `f` produce good outputs on example data; "inference" is calling that already-fixed function
on new input. This distinction — training changes parameters, inference does not — is the single
most load-bearing fact for a backend engineer, because it's exactly the line where your
infrastructure responsibilities usually start: you build systems that *serve* trained models
(inference), and training is often a different team's/pipeline's concern.

```python
# Conceptually, after training, a model is just a function with fixed parameters:
def predict(x: list[float], weights: list[float], bias: float) -> float:
    return sum(w * xi for w, xi in zip(weights, x)) + bias
    # `weights` and `bias` were learned; this function itself never changes at inference time
```

## Loss functions: how "good" gets measured during training

A loss function scores how wrong a prediction is versus the true label; training is the process of
adjusting parameters to make average loss smaller over the training set (via gradient descent —
you don't need to implement this, but you should know the name and the one-sentence idea: nudge
each parameter in the direction that reduces loss, repeat). Different tasks use different losses:
mean squared error for regression, cross-entropy for classification — knowing *which loss goes with
which task* is a more useful fact for you than the calculus behind gradient descent.

## Overfitting vs. underfitting — the concept interviewers probe hardest

- **Overfitting**: the model fits the training data very well but performs poorly on new data — it
  memorized noise/specifics of the training set instead of learning the general pattern. Classic
  symptom: training accuracy high, validation/test accuracy much lower.
- **Underfitting**: the model performs poorly on *both* — it's too simple (or undertrained) to
  capture the pattern at all.
- **Why this matters for a backend engineer**: overfitting is why you'll see references to
  train/validation/test splits, regularization, and dropout in ML code you deploy — and why a
  model that looked great in an offline eval can degrade in production if the production data
  distribution drifts from what it was trained/validated on (a real operational concern you may
  own: monitoring for this drift).

## Train / validation / test — why three splits, not one

| Split | Purpose |
|---|---|
| Train | Parameters are fit directly on this data |
| Validation | Used to tune hyperparameters and detect overfitting *during* development — the model never trains directly on it |
| Test | Held out until the very end, used once for a final unbiased performance estimate |

The practical failure mode to know: if you tune hyperparameters against the test set repeatedly,
you've effectively leaked test-set information into your decisions, and the "final" number is
optimistic — this is why a strict train/val/test separation (and sometimes a completely separate
held-out set for the final report) matters, and why "we kept re-checking against the test set" is
a red flag if you hear it in a design discussion.

## Supervised vs. unsupervised vs. reinforcement learning (one line each)

- **Supervised**: learn `f(x) → y` from labeled examples (most production ML you'll encounter as a
  backend engineer — classification, regression).
- **Unsupervised**: find structure in unlabeled data (clustering, dimensionality reduction) — less
  common in typical backend-adjacent work, but embeddings/clustering come up in search/recommendation
  systems.
- **Reinforcement learning**: an agent learns by taking actions and receiving reward signals — the
  training approach behind RLHF used to align LLMs; know the name and rough idea (model generates
  output, a reward signal — often derived from human preference data — nudges it toward preferred
  outputs) since it comes up when discussing how modern LLMs were trained, even though you won't
  implement RL yourself.

## Classification vs. regression

Classification predicts a discrete label (spam/not-spam, which of N categories); regression
predicts a continuous number (price, ETA). Same underlying training process, different loss
function and different output layer — worth knowing because it determines what a model's raw
output actually *is* (probabilities over classes vs. a single number), which matters when you're
writing the code that consumes a model's output in a backend service.

## Interview questions

**Q: In one paragraph, what's the difference between training and inference, and why does that
distinction matter for someone building the serving infrastructure?**
A: Training searches for parameter values using labeled data and a loss function; inference calls
the already-fixed function on new input with no further learning. It matters for infrastructure
because inference is typically latency-sensitive, high-throughput, and read-only with respect to
the model — very different operational requirements (autoscaling, caching, batching) than the
training pipeline, which is usually a separate, less latency-sensitive batch/offline system.

**Q: A model has 99% training accuracy and 60% validation accuracy. What's happening and what
would you ask the ML team?**
A: Classic overfitting — the model memorized training-set specifics rather than generalizing.
Reasonable questions: how much training data exists (small datasets overfit more easily), is
regularization/dropout being used, is the validation set actually representative of production
data (a distribution mismatch can look like overfitting but isn't the same problem).

**Q: Why would a model that performed well in offline evaluation degrade after being deployed to
production?**
A: Distribution drift — production input data no longer matches the distribution the model was
trained/validated on (new user behavior, seasonal effects, upstream data schema changes). This is
an operational monitoring concern, not a one-time training problem — see
[`../09_ai_backend_and_llm_systems/06_model_evaluation.md`](../09_ai_backend_and_llm_systems/06_model_evaluation.md)
for the production-monitoring side of this.

## Exercises

1. Write one paragraph, in your own words, explaining overfitting to a non-ML engineer on your
   team who's asking why a model needs a separate validation set instead of just training accuracy.
2. Given a hypothetical model that classifies support tickets into 5 categories, name which split
   (train/val/test) you'd use to (a) decide how many training epochs to run, (b) report final
   accuracy to stakeholders, (c) fit the model's weights.
