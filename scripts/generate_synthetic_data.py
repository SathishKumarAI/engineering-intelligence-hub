"""Synthetic engineering corpus generator (the code used to produce data/).

Generates plausible-looking but ENTIRELY FICTIONAL internal engineering documents
(an RFC, a runbook, an ADR, an API reference) so the project runs out of the box
without exposing any real internal docs. Values are illustrative only.

Usage:
    python scripts/generate_synthetic_data.py            # writes the default corpus
    python scripts/generate_synthetic_data.py --seed 7   # reproducible variation

Deterministic given a seed: no LLM, no network — templates + a seeded RNG.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

DISCLAIMER = "> SYNTHETIC SAMPLE — fictional internal doc for demo/testing only.\n"


def rfc_rate_limiting(rng: random.Random) -> tuple[str, str]:
    rpm = rng.choice([100, 120, 200])
    body = f"""# RFC-0001: API Rate Limiting (synthetic sample)

{DISCLAIMER}
## Status
Accepted.

## Summary
Introduce per-API-key rate limiting on the public API gateway using a token-bucket
algorithm.

## Decision
- Default limit: {rpm} requests per minute per API key.
- Burst capacity equals the per-minute limit; tokens refill continuously.
- Exceeding the limit returns HTTP 429 with a `Retry-After` header.
- Unauthenticated requests are limited by client IP at half the authenticated rate.

## Rationale
Token bucket allows short bursts while bounding sustained load. Limits are enforced at
the gateway so individual services don't each reimplement throttling.
"""
    return "rfc_0001_rate_limiting.md", body


def runbook_deploy(rng: random.Random) -> tuple[str, str]:
    body = """# Runbook: Deploy and Rollback (synthetic sample)

{disc}
## Deploy
1. Merge to `main`; CI builds and pushes the image tagged with the commit SHA.
2. `kubectl set image deploy/api api=registry/api:<sha>`.
3. Watch rollout: `kubectl rollout status deploy/api`.

## Rollback
- To undo the most recent deploy: `kubectl rollout undo deploy/api`.
- To roll back to a specific revision: `kubectl rollout undo deploy/api --to-revision=<n>`.
- List revisions with `kubectl rollout history deploy/api`.

## Health
- Liveness: `GET /health`. Readiness: `GET /ready`.
- If readiness fails after rollback, check the database migration state before retrying.
""".format(disc=DISCLAIMER)
    return "runbook_deploy_rollback.md", body


def adr_database(rng: random.Random) -> tuple[str, str]:
    body = """# ADR-0007: Use PostgreSQL as the primary datastore (synthetic sample)

{disc}
## Status
Accepted.

## Context
We need a primary datastore for transactional data with strong consistency and
relational queries across orders, users, and inventory.

## Decision
Use PostgreSQL as the primary datastore. Use a managed instance with automated backups
and point-in-time recovery.

## Alternatives considered
- A document database was rejected because our access patterns are relational and we
  need multi-row transactions.

## Consequences
- Schema migrations are required and run in CI before deploy.
- Read replicas can be added later for read-heavy endpoints.
""".format(disc=DISCLAIMER)
    return "adr_0007_postgres.md", body


def api_reference(rng: random.Random) -> tuple[str, str]:
    ttl = rng.choice([15, 30, 60])
    body = f"""# Public API Reference (synthetic sample)

{DISCLAIMER}
## Authentication
All requests require an `Authorization: Bearer <token>` header. Tokens are issued by
the auth service and expire after {ttl} minutes; refresh via `POST /v1/auth/refresh`.

## Errors
- `401` — missing or expired token.
- `429` — rate limit exceeded (see RFC-0001); honour the `Retry-After` header.
- `5xx` — retry with exponential backoff.

## Pagination
List endpoints accept `?page=` and `?limit=` (max 100). Responses include a
`next_page` cursor when more results exist.
"""
    return "api_reference.md", body


GENERATORS = [rfc_rate_limiting, runbook_deploy, adr_database, api_reference]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for gen in GENERATORS:
        name, body = gen(rng)
        (DATA_DIR / name).write_text(body, encoding="utf-8")
        print(f"wrote data/{name}")


if __name__ == "__main__":
    main()
