<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-02

Summary:
- Finalized migration from Cloudflare/stlite to Streamlit Community Cloud + Supabase.
- Unified embedding logic using Hugging Face Inference API.
- Cleaned up legacy scripts, configuration, and documentation.
- Updated project guidelines and setup instructions.
- Prepared for commit and push.

Next Steps:
- Port SQLite logic to PostgreSQL (Supabase).
- Implement GitHub OAuth using `streamlit-oauth`.
- Implement optimistic locking for concurrent record editing.
- Implement automated embedding regeneration in the application logic.

Completed Tasks:
- UPDATED dev Docker setup to use HF free inference exclusively for embeddings.
- UPDATED `scripts/test_embeddings.py` to target Hugging Face Inference API.
- CONFIGURED Hugging Face API token in `.streamlit/secrets.toml` and `.env` after interactive setup.
- UPDATED `docs/development/EMBEDDINGS.md` with explicit Classic/Read token setup instructions.
- SET UP `.streamlit/secrets.toml` based on `.env` and ensured it is ignored by git.
- EVALUATED ModernBERT vs BGE-M3 for embeddings; confirmed BGE-M3 is superior for multilingual/Algonquian context.
- MIGRATED architecture from Cloudflare Workers/stlite to Streamlit Community Cloud/Supabase.
- Updated core AI Guidelines (`.junie/guidelines.md`) with the new tech stack.
- Updated `docs/development/roadmap.md` with the new setup and deployment flow.
- Updated `README.md` with the new tech stack and quick start guide.
- Removed legacy Cloudflare and stlite references across documentation and scripts.
- Updated `pyproject.toml` to reflect new dependencies and remove `cloudflare`.
- Updated `docker/docker-compose.yml` to reflect Streamlit-based stack.
- ADDED embedding regeneration lifecycle documentation to `docs/development/EMBEDDINGS.md`.
- COMMITTED and PUSHED migration and cleanup changes.
