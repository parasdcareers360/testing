# Chunking Strategies

> **Type:** Study notes

## Why interviewers ask this

Chunking is the least glamorous and most underestimated part of a RAG pipeline — get it wrong and no
amount of retrieval or prompting tuning downstream can fix it. Interviewers ask about it to see
whether you understand chunking as a **retrieval-quality decision**, not a mechanical text-splitting
step, and whether you'd adapt strategy to document type rather than using one fixed-size splitter
everywhere.

## Why chunking exists at all

Two forcing constraints: embedding models have an input token limit (can't embed an entire 50-page
document as one vector meaningfully — long inputs get compressed into one vector that loses
fine-grained detail), and the LLM's context window is finite, so you want to retrieve and pass only
the *relevant* portion of a document, not the whole thing. Chunk size is a direct trade-off between
these: too large and retrieval is imprecise (a chunk "about many things" scores moderately for many
queries, precisely for none) and wastes context budget; too small and you lose surrounding context
needed to make sense of the chunk on its own, and increase the count of chunks (and thus embedding
calls, storage, retrieval overhead).

## Fixed-size chunking (with overlap)

```python
def fixed_size_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # step back so context isn't lost at the boundary
    return chunks
```

Simple, predictable, works reasonably as a default. **Overlap** (here, 50 chars) exists because a
sentence or idea that straddles a chunk boundary would otherwise be split so neither chunk contains
it intact — overlap means the boundary region appears in both neighboring chunks, so at least one of
them has it whole. Typical overlap is 10-20% of chunk size.

**Downside**: splits purely on character/token count with no regard for sentence, paragraph, or
semantic boundaries — can cut a sentence, a code block, or a table row in half, which measurably
hurts both retrieval relevance (a half-sentence chunk embeds ambiguously) and the LLM's ability to
use the chunk correctly.

## Structure-aware chunking (the better default for most real documents)

Split on natural document boundaries first (paragraphs, headings, list items, code blocks), and only
fall back to fixed-size splitting within an oversized block:

```python
import re

def structure_aware_chunks(markdown_text: str, max_chunk_size: int = 800) -> list[str]:
    # Split on markdown headers and paragraph breaks first
    sections = re.split(r"\n(?=#{1,3} )", markdown_text)
    chunks = []
    for section in sections:
        if len(section) <= max_chunk_size:
            chunks.append(section.strip())
        else:
            paragraphs = section.split("\n\n")
            buffer = ""
            for para in paragraphs:
                if len(buffer) + len(para) > max_chunk_size:
                    if buffer:
                        chunks.append(buffer.strip())
                    buffer = para
                else:
                    buffer += "\n\n" + para
            if buffer:
                chunks.append(buffer.strip())
    return [c for c in chunks if c]
```

This respects headings and paragraph breaks as the primary split points, only falling back to
size-based splitting for an oversized single section — the resulting chunks are far more likely to
be coherent, self-contained units of meaning.

## Semantic chunking

A more advanced approach: embed sentences (or small groups), then split where the semantic
similarity between consecutive sentences drops sharply (a topic shift), rather than at a fixed size
or structural marker at all. Produces chunks that track actual topic boundaries but costs extra
embedding calls at chunking time and adds pipeline complexity. Worth naming as the state-of-the-art
option, but the honest, practical answer for most production systems: **structure-aware chunking
gets you 80% of the benefit for a fraction of the complexity**, and semantic chunking is worth the
extra cost mainly for corpora where documents genuinely lack usable structure (raw transcripts,
unstructured logs) and retrieval quality on structure-aware chunking has been measured and found
wanting.

## Document-type-specific strategies

| Document type | Strategy |
|---|---|
| Markdown/structured docs (this repo, API docs, wikis) | Structure-aware — split on headers, keep code blocks intact as single chunks regardless of size (splitting code mid-block is almost always worse than one oversized chunk) |
| PDFs / scanned documents | Extract text first (see [PDF pipeline](../06_system_design/exercises/pdf_ocr_processing_pipeline.md)), then structure-aware on the extracted text; watch for OCR artifacts breaking paragraph detection |
| Chat/support transcripts | Chunk by conversation turn or exchange, not by character count — a chunk should be a coherent Q&A pair or thread segment, not an arbitrary character window that might cut a question from its answer |
| Tables | Never split a table across chunks if avoidable — keep small tables as one chunk (with surrounding context/caption), or chunk per logical row group with the header repeated in each chunk so a retrieved row-chunk is still interpretable standalone |
| Code | Chunk by function/class boundary (via an AST-aware splitter or regex on `def`/`class`), never mid-function — a half-function chunk is close to useless both for embedding and for the LLM to reason about |

## Chunk metadata — what to attach beyond the text

```python
class DocumentChunk(models.Model):
    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    text = models.TextField()
    embedding = VectorField(dimensions=1536)
    chunk_index = models.IntegerField()          # position within the source document
    section_title = models.CharField(max_length=255, blank=True)  # nearest heading, if any
    embedding_model = models.CharField(max_length=100)
```

`chunk_index` lets you fetch neighboring chunks at query time (retrieve chunk N, also pull N-1/N+1
for more context — a common technique when a single chunk alone is too narrow) and `section_title`
lets you show the user *where* in the source document an answer came from, not just a raw text
snippet, which materially improves trust in a cited answer.

## Interview questions

**Q: Your RAG system retrieves the right document but the LLM's answer is still incomplete — why
might chunking be the cause even though retrieval worked?**
The relevant information may have been split across two chunks by the chunking strategy, and only
one made it into the top-K retrieved set — the answer exists in the source document but not
contiguously in any single retrieved chunk. Fix: increase overlap, switch to structure-aware
chunking that keeps related content together, or retrieve neighboring chunks (`chunk_index ± 1`) in
addition to the top match.

**Q: How would you chunk a document containing large tables (e.g. a pricing sheet) for a RAG system
that needs to answer questions about specific rows?**
Never split a table mid-row-group; either treat a reasonably-sized table as one atomic chunk (with
context/caption preserved) or chunk per logical row group with the column headers repeated in each
chunk, so a retrieved chunk is self-interpretable without needing the header from elsewhere in the
document.

**Q: What's the trade-off in choosing a smaller vs. larger chunk size?**
Smaller chunks: more precise retrieval (each chunk about one specific thing, so similarity scores
discriminate better) but risk losing surrounding context and multiply the number of chunks (more
embedding calls, more storage, more retrieval candidates to rank). Larger chunks: more context per
chunk but blunter similarity discrimination (a chunk "about many things" ranks moderately for many
queries) and wastes prompt budget on irrelevant portions of a partially-relevant chunk.

## Exercise

Take a real markdown document (e.g. one of this curriculum's own topic files) and chunk it three
ways: fixed-size (500 chars, 50 overlap), structure-aware (split on headers), and by paragraph only.
Compare the resulting chunk boundaries by eye — identify at least one place where fixed-size
chunking splits something structure-aware chunking kept intact.
