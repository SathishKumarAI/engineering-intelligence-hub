# Public API Reference (synthetic sample)

> SYNTHETIC SAMPLE — fictional internal doc for demo/testing only.

## Authentication
All requests require an `Authorization: Bearer <token>` header. Tokens are issued by
the auth service and expire after 30 minutes; refresh via `POST /v1/auth/refresh`.

## Errors
- `401` — missing or expired token.
- `429` — rate limit exceeded (see RFC-0001); honour the `Retry-After` header.
- `5xx` — retry with exponential backoff.

## Pagination
List endpoints accept `?page=` and `?limit=` (max 100). Responses include a
`next_page` cursor when more results exist.
