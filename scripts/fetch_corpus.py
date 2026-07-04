#!/usr/bin/env python3
"""Fetch a real, open corpus for the software-engineering domain (feature F22).

Source: **arXiv API** — open-access scholarly papers. We query the Software
Engineering (``cs.SE``) and Distributed / Parallel Computing (``cs.DC``) categories
and save each paper's title + abstract. arXiv abstracts are open access and freely
redistributable, so this corpus is safe to ship in a public repo. It gives the
engineering RAG realistic technical prose (design trade-offs, systems, distributed
computing) without shipping anyone's private internal docs.

Design:
- **stdlib only** (urllib + xml.etree) — no extra dependency, runs anywhere.
- **Idempotent** — skips files already present; re-run to add new papers only.
- **Polite** — sends a descriptive User-Agent and rate-limits requests (arXiv asks
  for >=3s between calls).
- **Offline-safe** — network errors are logged and skipped, never fatal (CI-friendly).
- **Provenance** — every download is recorded in ``data/SOURCES.md`` with its URL.

Usage:
    python scripts/fetch_corpus.py                 # fetch defaults into data/corpus/
    python scripts/fetch_corpus.py --limit 10      # at most 10 papers total
    python scripts/fetch_corpus.py --dry-run       # list what would be fetched

Override the descriptive contact (a GitHub URL is fine):
    ARXIV_USER_AGENT="my-project (github.com/you)" python scripts/fetch_corpus.py
"""

from __future__ import annotations

import argparse
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
SOURCES_FILE = PROJECT_ROOT / "data" / "SOURCES.md"

# arXiv asks for a descriptive UA that identifies the requester. Only a public GitHub
# handle is used — no personal contact details in the repo.
USER_AGENT = os.environ.get(
    "ARXIV_USER_AGENT", "rag-learning-companion (github.com/SathishKumarAI)"
)
API_BASE = "http://export.arxiv.org/api/query"
RATE_LIMIT_SECONDS = 3.0  # arXiv asks callers to wait >=3s between requests.

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

# A few focused queries over Software Engineering (cs.SE) and Distributed / Parallel
# Computing (cs.DC) — the categories closest to internal RFCs, runbooks and ADRs.
# Each entry is (label, search_query, max_results).
QUERIES: list[tuple[str, str, int]] = [
    ("cs.SE", "cat:cs.SE", 8),
    ("cs.DC", "cat:cs.DC", 8),
    ("cs.SE+cs.DC", "cat:cs.SE+OR+cat:cs.DC", 8),
]

_WS_RE = re.compile(r"[ \t]{2,}")
_NL_RE = re.compile(r"\n{3,}")
_ID_RE = re.compile(r"([0-9]{4}\.[0-9]{4,5})(v[0-9]+)?$")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed arXiv host
        return resp.read()


def _clean(text: str) -> str:
    text = text.replace("\r", "")
    text = "\n".join(line.strip() for line in text.splitlines())
    text = _WS_RE.sub(" ", text)
    return _NL_RE.sub("\n\n", text).strip()


def _arxiv_id(entry_id: str) -> str | None:
    """Extract a bare arXiv id (e.g. ``2401.01234``) from an entry <id> URL."""
    m = _ID_RE.search(entry_id.strip())
    return m.group(1) if m else None


def query_entries(search_query: str, max_results: int) -> list[dict[str, str]]:
    """Query the arXiv API and return parsed entries (id, title, abstract, url)."""
    params = urllib.parse.urlencode(
        {"search_query": search_query, "start": 0, "max_results": max_results},
        safe="+:",
    )
    raw = _get(f"{API_BASE}?{params}")
    root = ET.fromstring(raw)  # noqa: S314 - trusted arXiv Atom feed
    entries: list[dict[str, str]] = []
    for e in root.findall("atom:entry", ATOM_NS):
        entry_id = (e.findtext("atom:id", default="", namespaces=ATOM_NS) or "").strip()
        arxiv_id = _arxiv_id(entry_id)
        if not arxiv_id:
            continue
        title = _clean(e.findtext("atom:title", default="", namespaces=ATOM_NS) or "")
        abstract = _clean(e.findtext("atom:summary", default="", namespaces=ATOM_NS) or "")
        published = (
            e.findtext("atom:published", default="", namespaces=ATOM_NS) or ""
        ).strip()
        if not title or not abstract:
            continue
        entries.append(
            {
                "id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "published": published,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            }
        )
    return entries


def render(entry: dict[str, str]) -> str:
    return (
        f"# {entry['title']}\n\n"
        f"arXiv: {entry['id']}\n"
        f"Published: {entry['published']}\n"
        f"URL: {entry['url']}\n\n"
        f"## Abstract\n\n{entry['abstract']}\n"
    )


def record_source(arxiv_id: str, title: str, url: str) -> None:
    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    header = "# Corpus sources\n\nOpen, redistributable documents fetched by `scripts/fetch_corpus.py`.\n\n"
    if not SOURCES_FILE.exists():
        SOURCES_FILE.write_text(header, encoding="utf-8")
    line = f"- **arXiv:{arxiv_id}** ({title}, open access): {url}\n"
    existing = SOURCES_FILE.read_text(encoding="utf-8")
    if url not in existing:
        SOURCES_FILE.write_text(existing + line, encoding="utf-8")


def fetch(limit: int | None, dry_run: bool) -> int:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    seen: set[str] = set()
    for label, search_query, max_results in QUERIES:
        if limit is not None and saved >= limit:
            break
        try:
            entries = query_entries(search_query, max_results)
            time.sleep(RATE_LIMIT_SECONDS)
        except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError) as exc:
            print(f"WARN {label}: query failed ({exc}); skipping")
            continue
        for entry in entries:
            if limit is not None and saved >= limit:
                break
            arxiv_id = entry["id"]
            if arxiv_id in seen:
                continue
            seen.add(arxiv_id)
            dest = CORPUS_DIR / f"{arxiv_id}.txt"
            if dest.exists():
                print(f"skip {arxiv_id}: already present")
                continue
            if dry_run:
                print(f"would fetch {arxiv_id}: {entry['url']}")
                continue
            dest.write_text(render(entry), encoding="utf-8")
            record_source(arxiv_id, entry["title"], entry["url"])
            saved += 1
            print(
                f"saved {arxiv_id}: {len(entry['abstract']):,} chars "
                f"-> {dest.relative_to(PROJECT_ROOT)}"
            )
    return saved


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Fetch open engineering corpus (arXiv cs.SE / cs.DC abstracts)."
    )
    ap.add_argument("--limit", type=int, default=None, help="max papers to fetch total")
    ap.add_argument("--dry-run", action="store_true", help="list URLs, download nothing")
    args = ap.parse_args()
    n = fetch(args.limit, args.dry_run)
    if not args.dry_run:
        print(f"\nDone. {n} new document(s) in {CORPUS_DIR.relative_to(PROJECT_ROOT)}.")
        print("Next: python -m app.ingest  (re)builds the index over the new corpus.")


if __name__ == "__main__":
    main()
