<!-- Copyright (c) 2026 Brothertown Language -->

# Active Task

Date: 2026-02-01

- Scope: Re-evaluate and correct backend/src/backend/worker.py (Gemini mistakes)
- Changes this session:
  - Reverted GitHub OAuth token exchange to use POST with query-string parameters (works in our Worker runtime).
  - Added proper CORS headers and global OPTIONS preflight handling.
  - Avoided returning raw GitHub access token; emit JWT when JWT_SECRET is available.
  - Hardened D1 count result handling.
  - Added /api/health endpoint.
  - Fixed potential Worker hang during OAuth callback by:
    - Normalizing Response headers in error branches (no raw Python dicts to JS Response).
    - Adding AbortSignal timeouts to all outbound GitHub fetches.
- Next steps:
  - Enforce MDF validation on write endpoints and implement optimistic locking on updates.
  - Replace file-based seeding with environment-gated or admin-triggered import.

## Security note on JWT

- JWT issuance is recommended for protecting editor APIs. Without `JWT_SECRET`, the backend will not issue tokens, and protected routes will remain inaccessible to unauthenticated clients. Set `JWT_SECRET` (via bootstrap) and have the frontend include `Authorization: Bearer <jwt>` on subsequent requests.
