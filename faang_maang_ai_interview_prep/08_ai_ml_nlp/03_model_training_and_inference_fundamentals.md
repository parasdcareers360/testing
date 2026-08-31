# Model Training & Inference Fundamentals

> **Type:** Study notes

## Why interviewers ask this

An AI-backend engineer is far more likely to *operate* training and serving infrastructure than to
design a novel training loop — but you're expected to understand what the pipeline you're
operating is actually doing, so you can debug it, reason about its resource needs (GPU vs. CPU,
batch size, memory), and answer "why is this slow / expensive / wrong" questions credibly.

## The training loop, at the level you need to know it

1. **Forward pass**: input flows through the model, producing a prediction.
2. **Loss computation**: prediction is compared to the true label via a loss function.
3. **Backward pass (backpropagation)**: gradients of the loss with respect to every parameter are
   computed via the chain rule.
4. **Optimizer step**: parameters are nudged in the direction that reduces loss (gradient descent
   and its variants — Adam is the modern default in deep learning, generally converges faster and
   more reliably than plain SGD without much tuning).
5. Repeat over many **batches** (a subset of training data processed together) and **epochs** (one
   full pass over the training set).

You do not need to derive backpropagation's calculus for a backend-track interview — you need to
know this sequence exists, that "training" means iterating it many times, and that it's why
training is compute-intensive (many forward+backward passes) while inference is comparatively
cheap (forward pass only, once).

## Hyperparameters vs. parameters

- **Parameters**: learned from data during training (weights, biases) — you never set these
  directly.
- **Hyperparameters**: set before training and not learned (learning rate, batch size, number of
  epochs, number of layers) — chosen via experimentation, often against a validation set (see
  [`01_core_ml_concepts.md`](01_core_ml_concepts.md)).

The one hyperparameter worth understanding at a systems level: **batch size** directly trades off
training speed (larger batches = better GPU utilization, fewer steps per epoch) against memory
(larger batches need more GPU memory) and sometimes generalization (very large batches can converge
to sharper, less-generalizing minima) — this is exactly the kind of trade-off an infra engineer
gets asked about when a training job runs out of GPU memory.

## Inference: what actually happens when a model "runs"

At inference, the model's forward pass runs once per input (or once per batch of inputs) with
**parameters frozen** — no gradient computation, no backward pass, which is why frameworks expose
an explicit "eval/inference mode" that's meaningfully faster and lower-memory than training mode
(e.g. PyTorch's `model.eval()` + `torch.no_grad()` disables gradient tracking and dropout/batch-norm
training behavior).

```python
import torch

model.eval()                      # disable dropout, use running batch-norm stats
with torch.no_grad():             # skip building the computation graph for backprop
    predictions = model(input_batch)
```
Knowing to mention `torch.no_grad()` (or the equivalent "don't track gradients at inference"
concept in any framework) is a concrete, specific fact that signals real hands-on exposure rather
than textbook knowledge.

## Batching at inference — the systems-relevant part

Serving one request at a time under-utilizes GPU/accelerator hardware, which is built for
parallel matrix operations across a batch. Production inference services typically batch
concurrent requests together (with a small wait window, e.g. 5-20ms, to accumulate a batch) before
running one forward pass — this is a direct latency/throughput trade-off you'll actually design
around: too small a batching window wastes throughput, too large adds unacceptable per-request
latency. See
[`../09_ai_backend_and_llm_systems/13_cost_latency_throughput_batching_caching.md`](../09_ai_backend_and_llm_systems/13_cost_latency_throughput_batching_caching.md)
and
[`../09_ai_backend_and_llm_systems/15_model_serving_architecture.md`](../09_ai_backend_and_llm_systems/15_model_serving_architecture.md)
for the full serving-architecture treatment.

## CPU vs. GPU — the one-paragraph version you need

GPUs excel at the massively parallel matrix multiplications that dominate neural network
forward/backward passes; CPUs are better at branchy, sequential logic. Training large models is
essentially always GPU-bound; inference *can* run on CPU for small models or low-throughput use
cases (cheaper, simpler ops story — no GPU driver/CUDA version management), but large models
(LLMs, big vision models) need GPU (or specialized accelerators like TPUs) for acceptable latency
at any real throughput. As a backend engineer, the practical decision you'll actually face is
"does this endpoint need a GPU-backed instance, and if so, how do we keep it warm/utilized enough
to justify the cost" — GPU instances are expensive and often billed whether or not they're actively
computing.

## Fine-tuning vs. training from scratch (one paragraph, full treatment elsewhere)

Training a large model from scratch requires enormous data and compute, out of reach for nearly
every company outside a handful of AI labs. **Fine-tuning** takes an existing pretrained model and
continues training it (often on a smaller, task-specific dataset, sometimes with fewer parameters
updated via techniques like LoRA) to specialize it — this is the realistic option for most
companies, including AI-backend teams. Full trade-off discussion (fine-tuning vs. prompting/RAG)
lives in
[`../09_ai_backend_and_llm_systems/16_fine_tuning_vs_rag_tradeoffs.md`](../09_ai_backend_and_llm_systems/16_fine_tuning_vs_rag_tradeoffs.md)
— for most AI-backend roles, that file matters more to your interview than deep training-loop
mechanics.

## Interview questions

**Q: Why is inference much cheaper/faster than training for the same model?**
A: Training requires a forward pass, a backward pass (gradient computation via backprop), and an
optimizer step, repeated over many batches and epochs. Inference is a forward pass only, run once,
with parameters frozen and gradient tracking disabled — no backward pass, no repeated iteration.

**Q: A training job is running out of GPU memory. What levers would you pull, and what do they
cost?**
A: Reduce batch size (slower training, more steps per epoch, but less memory per step); use
gradient accumulation (simulate a larger effective batch size across several smaller forward/backward
passes before an optimizer step, trading time for memory); use mixed-precision training (lower
numerical precision, less memory, usually minimal accuracy impact); or move to a larger-memory GPU
instance (higher cost). Naming multiple levers and their trade-offs is the point — there's rarely
one "correct" answer.

**Q: Why do production inference services batch requests instead of processing them one at a
time?**
A: GPU/accelerator hardware is built for parallel operations across a batch; single-request
inference under-utilizes it. Batching (with a small accumulation window) trades a small amount of
added per-request latency for significantly better throughput and cost efficiency — the window
size is a latency/throughput tuning knob.

## Exercises

1. Explain, in your own words to a non-ML teammate, why a model needs `model.eval()` (or the
   equivalent) switched on for serving and what would go subtly wrong if it were left in training
   mode in production.
2. Given a hypothetical inference endpoint receiving 200 requests/second, each processed
   individually with no batching, sketch (in words, not code) what you'd change and what trade-off
   you'd be making.
