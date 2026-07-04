"""Offline tests for the F22 arXiv corpus fetcher's pure helpers (no network)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("fetch_corpus", ROOT / "scripts" / "fetch_corpus.py")
fetch_corpus = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch_corpus)  # type: ignore[union-attr]

_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.01234v1</id>
    <title>Resilient Microservice Deployment</title>
    <summary>An abstract about distributed systems   and rollback strategies.</summary>
    <published>2024-01-02T00:00:00Z</published>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.09999v1</id>
    <title></title>
    <summary>Missing title, should be skipped.</summary>
    <published>2024-01-03T00:00:00Z</published>
  </entry>
</feed>"""


def test_arxiv_id_extraction():
    assert fetch_corpus._arxiv_id("http://arxiv.org/abs/2401.01234v2") == "2401.01234"
    assert fetch_corpus._arxiv_id("http://arxiv.org/abs/2401.01234") == "2401.01234"
    assert fetch_corpus._arxiv_id("not-an-id") is None


def test_clean_collapses_whitespace_and_blank_lines():
    assert fetch_corpus._clean("a   b\n\n\n\nc") == "a b\n\nc"


def test_query_entries_parses_and_skips_incomplete(monkeypatch):
    monkeypatch.setattr(fetch_corpus, "_get", lambda url: _FEED)
    entries = fetch_corpus.query_entries("cat:cs.SE", 5)
    assert len(entries) == 1  # the title-less entry is dropped
    e = entries[0]
    assert e["id"] == "2401.01234"
    assert e["title"] == "Resilient Microservice Deployment"
    assert "rollback strategies" in e["abstract"]
    assert e["url"] == "https://arxiv.org/abs/2401.01234"


def test_render_contains_key_fields():
    entry = {
        "id": "2401.01234", "title": "A Systems Paper", "abstract": "Body.",
        "published": "2024-01-02T00:00:00Z", "url": "https://arxiv.org/abs/2401.01234",
    }
    out = fetch_corpus.render(entry)
    assert "# A Systems Paper" in out
    assert "arXiv: 2401.01234" in out
    assert "## Abstract" in out
