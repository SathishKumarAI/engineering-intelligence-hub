# RFC-0001: API Rate Limiting (synthetic sample)

> SYNTHETIC SAMPLE — fictional internal doc for demo/testing only.

## Status
Accepted.

## Summary
Introduce per-API-key rate limiting on the public API gateway using a token-bucket
algorithm.

## Decision
- Default limit: 120 requests per minute per API key.
- Burst capacity equals the per-minute limit; tokens refill continuously.
- Exceeding the limit returns HTTP 429 with a `Retry-After` header.
- Unauthenticated requests are limited by client IP at half the authenticated rate.

## Rationale
Token bucket allows short bursts while bounding sustained load. Limits are enforced at
the gateway so individual services don't each reimplement throttling.
