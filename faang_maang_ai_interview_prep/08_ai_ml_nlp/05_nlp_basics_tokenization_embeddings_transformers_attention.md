# NLP Basics: Tokenization, Embeddings, Transformers, Attention

> **Type:** Study notes

## Why interviewers ask this

This is the bridge file between general ML and the LLM-systems content in
[`../09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/) — you cannot reason
credibly about chunking strategy, embedding pipelines, or context-window limits without these four
concepts. An AI-backend interviewer expects fluency here even if you'll never train a transformer
yourself, because these concepts directly explain *why* LLM systems behave and cost the way they
do (context length limits, embedding dimensionality, token-based pricing).

## Tokenization — text isn't processed as words or characters

Models don't operate on raw text; they operate on integer token IDs from a fixed vocabulary.
Modern LLMs use **subword tokenization** (Byte-Pair Encoding or similar) rather than whole-word or
character tokenization — it splits rare/unknown words into common subword pieces, so the
vocabulary stays a manageable fixed size (tens of thousands of tokens) while still being able to
represent any input text, including words never seen during training.

```python
# Conceptual (actual tokenizers use learned vocabularies, e.g. tiktoken for OpenAI models):
"unhappiness" → ["un", "happi", "ness"]     # rare whole word, but common subword pieces
"the" → ["the"]                             # common word, one token
```

**Why this matters practically**: a "token" is not a word — roughly 4 characters or ¾ of a word in
English on average — which is exactly why LLM context windows and API pricing are quoted in
tokens, not words or characters. Estimating token count from text length is a real, frequently-
needed calculation for cost/latency estimation — see
[`../09_ai_backend_and_llm_systems/13_cost_latency_throughput_batching_caching.md`](../09_ai_backend_and_llm_systems/13_cost_latency_throughput_batching_caching.md).

## Embeddings — turning text into vectors that capture meaning

An embedding is a dense vector (typically hundreds to a few thousand dimensions) representing a
piece of text such that **semantically similar text produces vectors that are close together** in
that vector space (measured by cosine similarity or dot product). This single idea underlies
semantic search, RAG retrieval, recommendation, and clustering — the entire premise of
[`../09_ai_backend_and_llm_systems/01_vector_databases_and_similarity_search.md`](../09_ai_backend_and_llm_systems/01_vector_databases_and_similarity_search.md).

```python
# Conceptual — a real embedding model (e.g. OpenAI's text-embedding-3, or a
# sentence-transformers model) produces vectors, not this toy example:
embed("a dog ran in the park")   → [0.12, -0.05, 0.88, ...]   # 1536-dim, e.g.
embed("a puppy played outside")  → [0.14, -0.03, 0.85, ...]   # close to the above — similar meaning
embed("stock market rose today") → [-0.90, 0.44, -0.12, ...]  # far from both — unrelated meaning
```

Word-level embeddings (Word2Vec, GloVe — older, worth knowing the names) gave one fixed vector per
word regardless of context; modern **contextual embeddings** (from transformer models) give a
different vector for the same word depending on surrounding context (`"bank"` in "river bank" vs.
"savings bank" gets different embeddings) — this shift is one of the reasons transformer-based
models represent meaning far better than older approaches.

## Attention — the mechanism that lets a model weigh relevant context

Attention lets a model, when processing one token, dynamically decide how much "weight" to give
every other token in the input when building that token's representation — rather than treating
all context equally or only looking at a fixed nearby window (as older RNN-based sequence models
effectively did). Conceptually: for each token, compute a relevance score against every other
token, turn those scores into weights (softmax), and combine other tokens' representations
weighted by relevance.

**Self-attention** specifically means a sequence attends to itself — every token can look at every
other token in the same input, which is why transformers handle long-range dependencies (a
pronoun near the end of a paragraph correctly referring to a noun near the beginning) far better
than earlier RNN architectures, which had to propagate information step-by-step through every
intervening token and tended to "forget" distant context.

**Why this matters practically for you**: attention's compute and memory cost scales
**quadratically with sequence length** (every token attends to every other token) — this is the
direct, concrete reason why longer context windows are expensive and why techniques like chunking
(see
[`../09_ai_backend_and_llm_systems/10_chunking_strategies.md`](../09_ai_backend_and_llm_systems/10_chunking_strategies.md))
and retrieval (RAG) exist as cost/latency mitigations rather than just always stuffing everything
into context.

## Transformers — the architecture, at the level you need

A transformer processes an entire input sequence in parallel (unlike RNNs, which process tokens
sequentially) using stacked layers of self-attention plus simple feed-forward networks, with
**positional encoding** added to the input embeddings so the model knows token *order* (attention
alone has no inherent sense of sequence position — it treats input as an unordered set of
weighted relationships unless position is explicitly encoded).

- **Encoder-only** (e.g. BERT-style): builds a rich contextual representation of input text — good
  for classification, embeddings, search relevance — doesn't generate new text token-by-token.
- **Decoder-only** (e.g. GPT-style, the architecture behind most modern chat LLMs): generates text
  autoregressively — predicts the next token given all previous tokens, feeds that token back in,
  repeats. This is why LLM responses stream token-by-token and why generation latency scales with
  output length (see
  [`../09_ai_backend_and_llm_systems/05_streaming_responses.md`](../09_ai_backend_and_llm_systems/05_streaming_responses.md)).
- **Encoder-decoder** (e.g. T5, translation models): encodes input fully, then decodes an output
  sequence conditioned on that encoding — common for translation/summarization-style tasks.

You do not need to derive the attention formula (`softmax(QKᵀ/√d)V`) from scratch for a backend
interview, but recognizing that notation and being able to say what Q (query), K (key), and V
(value) conceptually represent — "for each token, compare its query against every token's key to
get relevance weights, then combine values by those weights" — signals real understanding beyond
buzzword familiarity.

## Interview questions

**Q: Why do LLM providers price and limit usage in "tokens" rather than words or characters?**
A: Because that's the actual unit the model processes — subword tokenization means a token isn't
a fixed unit of text (roughly ¾ of a word in English on average, but varies by language and
content), so tokens are the accurate cost/capacity measure; a word or character count would be a
poor proxy.

**Q: Why is attention's cost quadratic in sequence length, and what's the practical consequence?**
A: Every token attends to every other token, so pairwise comparisons scale as O(n²) in sequence
length n. Practical consequence: doubling context length roughly quadruples attention compute,
which is why very long contexts are expensive/slow, and why RAG (retrieve only relevant chunks
instead of stuffing everything into context) and chunking strategies exist as mitigations.

**Q: What's the practical difference between an encoder-only model and a decoder-only model, and
when would you use each in a system you're building?**
A: Encoder-only models produce rich representations of input text without generating new text —
use them for embeddings/semantic search/classification. Decoder-only models generate text
autoregressively — use them for chat, completion, summarization-as-generation. A RAG system
typically uses an encoder-style embedding model for retrieval and a decoder-style LLM for the
actual generated answer — two different models doing two different jobs.

## Exercises

1. Take three short sentences (two semantically similar, one unrelated) and, without calling an
   actual embedding API, predict which pair would have the highest cosine similarity — then
   explain, in your own words, what "cosine similarity between embeddings" is actually measuring.
2. Explain in 2-3 sentences why a longer context window in an LLM API is both more expensive per
   request and slower, tying the explanation directly to attention's computational cost.
