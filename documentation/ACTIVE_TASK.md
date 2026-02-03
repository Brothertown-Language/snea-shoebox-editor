<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-02

- Updated documentation to mark semantic search as a deferred future feature due to budget constraints.
- Explicitly clarified that the long-term goal is **static cross-linked semantic relationships**, which eliminates the need for live embedding or real-time vector database maintenance.
- Updated `docs/development/EMBEDDINGS.md`, `tests/embeddings/final_report.md`, and `documentation/EMBEDDING_EVAL_WORKFLOW.md` with these architectural details.
- Completed embedding model evaluation (1000 samples) and documented findings for future research.
- HF inference tests were hanging during implementation attempts, confirming the decision to defer.
- Finalized migration from Cloudflare/stlite to Streamlit Community Cloud + Supabase.
- Prepared AI-agent-ready workflow for future embedding evaluation and fine-tuning.
- Cleaned up legacy scripts, configuration, and documentation.
- Updated project guidelines and setup instructions.
- Prepared for commit and push.

Next Steps:
- Execute embedding evaluation workflow:
    1. Generate stats in Docker: `USER_ID=$(id -u) GROUP_ID=$(id -g) USER_NAME=$(id -un) docker compose -f docker/docker-compose.yml run --rm evaluator python /app/docker.app/evaluate_models.py --output-dir /app/outputs` ✓
    2. Generate reports on host: `uv run python docker.app/generate_reports.py --data-dir docker.data --reports-dir docker.reports` ✓
- Execute fine-tuning on top-ranked model (E5-B) to improve Lemma-Gloss alignment.
- Port SQLite logic to PostgreSQL (Supabase) [Phase 3].
- Implement GitHub OAuth using `streamlit-oauth` [Phase 4].
- Implement optimistic locking for concurrent record editing.
- Implement Full-Text Search (FTS) in PostgreSQL [Phase 5].

Completed Tasks:
- ADDED `tests/embeddings/evaluate_models_tex.py` for model evaluation and LaTeX report generation with TikZ visualizations.
- UPDATED `docker/Dockerfile.eval` with non-root user, optimized layers, and virtual environment.
- UPDATED `docker/docker-compose.yml` with `evaluator` service and persistent Docker-managed volume `eval_data`.
- UPDATED documentation to include `docker-buildx` installation and BuildKit enablement instructions to resolve Docker legacy builder deprecation.
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
- UPDATED `docker.app/evaluate_models.py` to dynamically load model IDs from `docker.app/models-to-eval.md`.
- UPDATED `docker.app/generate_reports.py` to automatically generate a ranked Executive Summary in `master_report.tex` with automated pro/con analysis.
- COMMITTED and PUSHED migration and cleanup changes.
