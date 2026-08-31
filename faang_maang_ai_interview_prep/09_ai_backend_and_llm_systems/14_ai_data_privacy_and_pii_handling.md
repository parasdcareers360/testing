# AI Data Privacy & PII Handling

> **Type:** Study notes

## Why interviewers ask this

Sending user data to a third-party LLM API is a data-sharing decision with real compliance and
trust implications, on top of the usual backend privacy concerns — interviewers want to see that you
treat "call the LLM API" as **sending data to a third party**, not as an internal function call, and
that you know the concrete mitigations (redaction, zero-retention tiers, data minimization) rather
than a vague "we'd be careful with PII."

## Why LLM API calls are a distinct privacy concern

A normal internal service call keeps data inside your infrastructure boundary. An LLM API call sends
the prompt content — potentially including whatever user data is in context — to a third-party
provider's infrastructure. This raises questions that don't apply to internal calls: does the
provider retain the data, for how long, is it used for model training, and does sending it violate a
data-residency or a customer contractual commitment (many B2B contracts explicitly restrict where
customer data may be sent). Treat it with the same rigor as adding any new third-party data
processor — because that's exactly what it is.

## Data minimization — don't send what you don't need

The cheapest, most reliable mitigation: **only include in the prompt what the task actually needs**.
Summarizing a support ticket doesn't need the customer's full account history in context; classifying
a message's urgency doesn't need their email address. This is the same discipline as minimizing
fields in an API response — apply it to what goes into an LLM prompt, not just what comes back out.

```python
def build_summarization_prompt(ticket: Ticket) -> str:
    # Don't do this — passes the whole object including PII fields never needed for summarization:
    #   return f"Summarize: {ticket.__dict__}"
    # Do this — only what the task requires:
    return f"Summarize this support message:\n{ticket.body}"
```

## PII redaction before sending to the LLM

For tasks where the source content itself contains PII the task doesn't need (a support ticket body
mentioning a full name, phone number, or account number), redact before the API call:

```python
import re

PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}

def redact_pii(text: str) -> tuple[str, dict]:
    redacted = text
    found = {}
    for label, pattern in PII_PATTERNS.items():
        matches = pattern.findall(redacted)
        if matches:
            found[label] = len(matches)
            redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
    return redacted, found
```

**Be honest about the limits of regex-based redaction** in an interview: it reliably catches
structured PII (emails, phone numbers, SSNs, card numbers) but misses unstructured PII (a name
mentioned in prose, an address written in free text) — for those, either an NER (named-entity
recognition) model as a pre-processing pass, or a provider's dedicated PII-detection API, is the more
complete (though costlier) answer. State the trade-off rather than presenting regex redaction as a
complete solution — that overclaim is a real interview red flag in this specific area.

## Zero-retention / enterprise API tiers

Most major LLM providers offer enterprise agreements or API modes with **zero data
retention** (the request isn't stored after the response is returned, and isn't used for model
training) — distinct from a standard consumer product's default retention policy. When handling any
regulated or sensitive data (healthcare, financial, anything under contractual data-handling
commitments), verifying and using the zero-retention/no-training tier of the API (via the provider's
actual documented terms, not assumption) is a concrete, checkable requirement — worth naming
specifically that this is a contractual/API-configuration decision, not something prompting can
achieve.

## Data retention on your own side (logs, embeddings)

Privacy obligations don't stop at "don't send it to the provider unnecessarily" — your own logging
and storage of prompts/completions (see [LLM Observability](12_llm_observability.md)) and any
embeddings derived from user content are also data you're retaining and must handle under the same
policies as any other stored user data:
- Apply retention limits (auto-delete full prompt/completion logs after N days) rather than
  indefinite retention by default.
- Access-control the storage holding raw prompts/completions separately from general engineering
  log access — not everyone who can view latency dashboards needs to read user message content.
- Remember that **embeddings are a derived representation of the source text**, not an anonymized
  one — a vector can, in some cases, be partially inverted back toward the original text (embedding
  inversion is an active area of research) or at minimum still constitutes personal data under
  regulations like GDPR if it's derived from personal data. Deleting a user's source data (a "right
  to be forgotten" request) means also deleting their derived embeddings/chunks, not just the
  original row.

## GDPR/CCPA-style "right to be forgotten" in a RAG system

A concrete, checkable requirement: when a user's data must be deleted, the deletion needs to cascade
to every derived artifact, not just the source row:

```python
def handle_deletion_request(document_id: int):
    document = Document.objects.get(id=document_id)
    DocumentChunk.objects.filter(document=document).delete()   # vectors, not just source text
    # If a vector DB is used separately from Postgres (dual-write setup — see
    # 01_vector_databases_and_similarity_search.md), also delete there explicitly:
    vector_store.delete(namespace=document.tenant_id, filter={"document_id": document_id})
    # And purge any cached responses derived from this content:
    cache.delete_pattern(f"llm_response:*doc_{document_id}*")
    document.delete()
```

This is exactly why the dual-write problem (source of truth vs. separate vector store) discussed in
[Vector Databases](01_vector_databases_and_similarity_search.md) matters for compliance, not just
consistency — a deletion that only touches one store leaves personal data behind in the other.

## Interview questions

**Q: Your company is evaluating whether to build an LLM feature that processes customer support
tickets, which sometimes contain sensitive personal information. What do you check before shipping?**
Whether the LLM provider's terms (or the specific API tier being used) guarantee no data retention
and no training on submitted data; whether existing customer contracts restrict where/how customer
data can be processed (a new third-party processor may need customer/legal sign-off); and whether
redaction/minimization can reduce what's sent in the first place regardless of the provider's
policy, as defense in depth rather than relying solely on provider guarantees.

**Q: A user submits a GDPR deletion request. Their data was used to generate embeddings in your
RAG system months ago. What has to happen?**
Delete the source document/row, delete all derived chunk embeddings tied to it (in whichever store
holds them — Postgres/pgvector or a separate vector DB), and purge any cached LLM responses derived
from that content — a deletion that only removes the source row while embeddings/cached responses
persist doesn't actually fulfill the request.

**Q: Why is regex-based PII redaction not a complete solution, and what would you add?**
It only catches PII with a predictable structural pattern (emails, phone numbers, SSNs) and misses
unstructured PII like names or addresses embedded in free-form prose. A more complete approach adds
an NER model or a provider's dedicated PII-detection service as a pre-processing pass, layered with
regex for the cheap, high-confidence structured cases — state this as defense in depth, not claim
regex alone is sufficient.

## Exercise

Implement `redact_pii` above, run it against 10 realistic support-ticket-style sample messages
containing a mix of emails, phone numbers, and names in prose, and tabulate which PII types it
correctly redacts vs. misses — this exercise is specifically meant to make the "regex alone is
incomplete" point concrete rather than theoretical.
