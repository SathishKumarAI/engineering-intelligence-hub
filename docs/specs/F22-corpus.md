# Feature Spec — F22 Open-access corpus fetch

## Summary
A stdlib-only script that fetches a real, redistributable engineering corpus — recent
paper abstracts from the **arXiv API** (`cs.SE` Software Engineering, `cs.DC` Distributed
/ Parallel Computing) — so the RAG runs against genuine technical writing instead of only
synthetic samples.

## Problem / why
Demos and evals are more convincing on real technical prose, but the repo is public, so the
corpus must be freely redistributable. arXiv abstracts are open access; nobody's private
internal docs are shipped. The fetch has to be safe to run in CI (offline-tolerant) and safe
to re-run.

## Users & context
A developer/operator prep step, not part of the request path. Populates `data/corpus/`;
`python -m app.ingest` then (re)builds the index over it.

## Behaviour (acceptance criteria)
- WHEN `scripts/fetch_corpus.py` runs THEN for each configured query it calls the arXiv API,
  parses the returned Atom feed, and saves each paper's title + abstract as
  `data/corpus/<arxiv_id>.txt`.
- WHEN a target file already exists THEN it is skipped (idempotent — re-run adds only new papers).
- WHEN `--dry-run` is passed THEN it prints the URLs it would fetch and downloads nothing.
- WHEN `--limit N` is passed THEN at most N papers total are saved.
- WHEN a network/IO/parse error occurs THEN it is logged as `WARN` and skipped, never fatal (CI-friendly / offline-safe).
- WHEN a document is saved THEN it is recorded in `data/SOURCES.md` with its source URL (deduped).

## Rules / logic
- `app`-free, **stdlib only** (`urllib`, `xml.etree.ElementTree`, `re`) — no added dependency.
- `query_entries(search_query, max_results)` GETs `http://export.arxiv.org/api/query`, parses
  the Atom feed under the `atom:` namespace, and returns `(id, title, abstract, published, url)`
  per entry; the bare arXiv id is extracted from the entry `<id>` URL.
- `render` writes a small titled doc: title, arXiv id, published date, URL, then the abstract.
- **Polite / rate-limited**: sends a descriptive `User-Agent` (from `ARXIV_USER_AGENT`,
  defaulting to a public GitHub handle — no personal contact in the repo) and sleeps
  `RATE_LIMIT_SECONDS` (3.0s) between requests, per arXiv's request-rate guidance.
- **Provenance**: `record_source` appends a `- **arXiv:<id>** (<title>, open access): <url>`
  line to `data/SOURCES.md`, creating the file with a header on first write.
- Query set (`QUERIES`): `cat:cs.SE`, `cat:cs.DC`, and `cat:cs.SE+OR+cat:cs.DC`.

## Config / env knobs
- `ARXIV_USER_AGENT` — descriptive UA (a GitHub URL is fine).
- CLI: `--limit N`, `--dry-run`.

## Out of scope (for now)
- Full-text PDF extraction — title + abstract only (abstracts are enough to exercise the RAG
  and keep the corpus small and unambiguously redistributable).
- Non-arXiv sources (public RFCs, ADR catalogs) — could be added later behind the same shape.
- Sibling repos supply their **own** domain sources: finance uses SEC EDGAR 10-Ks; healthcare
  uses PubMed Central Open Access + WHO/CDC. Only the source list differs; the stdlib-only,
  idempotent, rate-limited, provenance-recording shape is shared.

## Data touched
- Reads: arXiv API (public). Writes: `data/corpus/<arxiv_id>.txt`, `data/SOURCES.md`.

## Edge cases
- Query returning no usable entries (skipped with a message) · already-present file (skipped) ·
  duplicate URL in `SOURCES.md` (not re-appended) · duplicate paper across queries (deduped
  in-run) · malformed Atom (caught as `ParseError`, logged, skipped).

## Done when
- The script fetches real arXiv abstracts into `data/corpus/`, is idempotent and offline-safe,
  records provenance in `data/SOURCES.md`, and ships no copyrighted content — verified by a
  `--dry-run` that lists URLs and a re-run that skips existing files.
