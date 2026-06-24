# Glossary

Shared vocabulary so humans and the agent use the same words.

| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-Augmented Generation — retrieve relevant text, then have an LLM answer from it. |
| **chunk** | A slice of a source document (≈1000 chars) that is embedded and stored. Retrieval works on chunks, not whole files. |
| **embedding** | A numeric vector representing a chunk's meaning; similar text → nearby vectors. |
| **vector store** | The database of embeddings (Chroma here) that supports similarity search. |
| **retrieval / top-k** | Fetching the `k` chunks most similar to the question. |
| **grounding** | Answering only from retrieved passages; if they don't cover it, say so. |
| **citation** | A `[n]` marker in the answer pointing at a specific retrieved chunk, surfaced with its source filename + snippet. |
| **provider** | The swappable model backend: `ollama` (open-source, default) or `claude`. |
| **faithfulness** | Eval metric: is every claim in the answer supported by the retrieved context? |
| **hit-rate** | Eval metric: did the expected source appear in the top-k retrieved chunks? |
| **ingest** | The pipeline that loads → chunks → embeds → persists documents. |

### Domain terms (engineering docs)
| Term | Meaning |
|------|---------|
| **RFC** | Request for Comments — a proposal for a significant change. |
| **ADR** | Architecture Decision Record — a decision + its rationale + alternatives. |
| **runbook** | Step-by-step operational procedure (e.g. deploy/rollback). |
| **rollout / rollback** | Shipping a new version / reverting to a previous one. |
| **rate limit** | A cap on requests per client over time (e.g. 120/min). |

> All docs in `data/` are **synthetic and fictional** — they do not describe a real system.
