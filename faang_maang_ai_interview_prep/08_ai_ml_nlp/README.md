# 08 — AI/ML & NLP Fundamentals (for a Backend Engineer)

> **Type:** Study notes (index)

This module is deliberately narrow: **what a 3-YOE Python backend engineer needs to know about
ML/NLP to pass an AI-company backend/platform interview**, not a machine learning curriculum. If
the role is "build and operate the systems that serve/host models" rather than "design and train
models," interviewers test whether you understand enough ML vocabulary and data flow to build
correct infrastructure around it — not whether you can derive backpropagation.

The practical, systems-level counterpart to this module —
building RAG pipelines, integrating LLM APIs, vector databases, serving architecture — lives in
[`../09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/), which is where most of
an AI-backend interview's technical depth actually lands. Treat this module as the vocabulary and
mental models that make that module's content make sense, not as an end in itself.

## Contents

| # | Topic | File |
|---|---|---|
| 1 | Core ML concepts (what a model actually is, training vs. inference, overfitting) | [`01_core_ml_concepts.md`](01_core_ml_concepts.md) |
| 2 | Data preprocessing & feature engineering | [`02_data_preprocessing_and_feature_engineering.md`](02_data_preprocessing_and_feature_engineering.md) |
| 3 | Model training & inference fundamentals | [`03_model_training_and_inference_fundamentals.md`](03_model_training_and_inference_fundamentals.md) |
| 4 | NumPy / pandas / scikit-learn — what to actually know | [`04_numpy_pandas_sklearn_concepts.md`](04_numpy_pandas_sklearn_concepts.md) |
| 5 | NLP basics: tokenization, embeddings, transformers, attention | [`05_nlp_basics_tokenization_embeddings_transformers_attention.md`](05_nlp_basics_tokenization_embeddings_transformers_attention.md) |

## How to use this module

- **If your target role is pure backend (not AI-flavored)**: skip this module entirely, it won't
  come up.
- **If your target role is AI Backend Engineer / ML Platform Engineer**: read all five files once,
  then spend most of your remaining prep time in
  [`../09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/) — that's where the
  actual interview questions live for this role shape ("design a RAG pipeline," "how would you
  reduce hallucination," "how do you serve a model with low latency").
- **If you get an ML-research-flavored interview** (rare for a backend-track candidate, but
  possible at AI labs): this module is not sufficient preparation — say so honestly rather than
  bluffing depth you don't have; a backend candidate who clearly states "I know this at the
  systems/integration level, not the research level" reads better than one who fumbles a
  from-scratch backprop derivation.
