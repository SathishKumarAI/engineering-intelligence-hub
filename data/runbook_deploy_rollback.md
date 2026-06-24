# Runbook: Deploy and Rollback (synthetic sample)

> SYNTHETIC SAMPLE — fictional internal doc for demo/testing only.

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
