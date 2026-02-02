Make Docker-based BGE-M3 embeddings the source of truth for local development

Implemented comprehensive Docker-based embedding service using the same BAAI/bge-m3 model as Cloudflare production, with GPU acceleration for local development.

Changes:

Documentation Updates:
- Updated docs/development/EMBEDDINGS.md to make Docker-based local embedding service Option 1 (Recommended)
- Reorganized options: Docker+GPU (Option 1), Mock embeddings (Option 2), Remote dev worker (Option 3)
- Added detailed TEI (Text Embeddings Inference) configuration with GPU support
- Updated Local Testing Strategy to prioritize Docker embeddings for integration tests
- Updated docs/development/roadmap.md Phase 6 to reflect Docker as source of truth
- Added comprehensive embedding service section to docs/development/local-development.md
- Included prerequisites, setup instructions, testing procedures, and architecture details

Docker Configuration:
- Added embeddings service to docker/docker-compose.yml using ghcr.io/huggingface/text-embeddings-inference:1.5-cuda
- Configured NVIDIA GPU support with proper resource reservations
- Added health checks with extended startup period (120s) for model loading
- Added embedding_models volume for persistent model storage
- Updated backend service with USE_LOCAL_EMBEDDINGS and EMBEDDING_SERVICE_URL environment variables
- Made backend depend on embeddings service (optional dependency)

Helper Scripts:
- Created scripts/test_embeddings.py to verify embedding service functionality
- Tests health check, embedding generation, dimensionality (1024), consistency, and uniqueness
- Includes Algonquian word testing (wompan) for multilingual validation
- Created scripts/check_gpu.sh to verify GPU availability and Docker GPU support
- Checks NVIDIA GPU, drivers, Docker, NVIDIA Container Toolkit, and Docker Compose
- Provides detailed installation instructions for missing components
- Made check_gpu.sh executable

Environment Configuration:
- Created .env.example with comprehensive embedding service configuration
- Documented USE_LOCAL_EMBEDDINGS and EMBEDDING_SERVICE_URL variables
- Included local development notes with quick start commands
- Added fallback configuration for remote dev worker

System Verification:
- Verified local machine capabilities: RTX 3090 (24GB VRAM), 20 CPU cores, 62GB RAM
- Confirmed NVIDIA Container Toolkit is working
- Validated docker-compose.yml configuration syntax

This implementation ensures production parity by using the exact same BGE-M3 model locally as in Cloudflare, enabling developers to generate real embeddings with GPU acceleration for comprehensive integration testing.
