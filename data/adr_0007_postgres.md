# ADR-0007: Use PostgreSQL as the primary datastore (synthetic sample)

> SYNTHETIC SAMPLE — fictional internal doc for demo/testing only.

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
