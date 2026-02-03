<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Embedding Evaluation Workflow

## [GOAL: STATIC CROSS-LINKING]
The end goal for this evaluation is to select a model that can be fine-tuned on consumer hardware and used to build **static cross-linked semantic relationships**. These relationships will be referenced in the SNEA editor for linguist browsing and research.

**IMPORTANT ARCHITECTURE NOTES**:
- This feature **does NOT require live embedding** on the production site.
- It **does NOT require keeping the live database up-to-date for vector searching**.
- It focuses on generating offline/static discoveries that the editor can display without real-time AI overhead.

This document provides standardized instructions for AI agents to execute, resume, or restart the embedding model evaluation suite.

## Prerequisites

- **Environment**: Linux with NVIDIA GPU (16GiB+ VRAM recommended).
- **Tools**: Docker, `uv`.
- **Data**: `src/backend/seed_data/natick.txt` must be present.

## Architecture

1.  **Containerization**: All tests run in `docker/Dockerfile.eval` to ensure consistency.
2.  **Environment Management**: `uv` manages the virtual environment inside the container.
3.  **Data Extraction**: `scripts/extract_natick_samples.py` pulls test pairs.
4.  **Evaluation Core**: `tests/embeddings/evaluate_models.py` benchmarks models.

## Execution Steps

### 1. Build Evaluation Image
```bash
docker build -t snea-eval -f docker/Dockerfile.eval \
  --build-arg USER_ID=$(id -u) \
  --build-arg GROUP_ID=$(id -g) \
  --build-arg USER_NAME=$(whoami) .
```

### 2. Run Full Evaluation
This command runs the suite and persists results to the host filesystem. It uses a persistent Docker volume `snea-eval-cache` for both Hugging Face models and `uv` package cache to avoid re-downloading.

```bash
# Create persistent volume if it doesn't exist
docker volume create snea-eval-cache

# Run evaluation
docker run --rm --gpus all \
  -v $(pwd):/app \
  -v /tmp:/tmp \
  -v snea-eval-cache:/home/$(whoami)/.cache \
  -e UV_CACHE_DIR=/home/$(whoami)/.cache/uv \
  snea-eval /bin/bash -c "source /home/$(whoami)/.venv_eval/bin/activate && export PYTHONPATH=$PYTHONPATH:/app && uv run --python /home/$(whoami)/.venv_eval/bin/python --active python tests/embeddings/evaluate_models.py"
```

### 3. Analyze Results
The final report is generated at `tests/embeddings/final_report.md`.

## Resuming or Restarting Tests

### How to Restart
Simply run the **Run Full Evaluation** command above. The script `evaluate_models.py` is idempotent and will overwrite `tests/embeddings/final_report.md`.

### How to Resume (Partial Run)
To evaluate only specific models (e.g., if a previous run was interrupted):
1.  Modify the `models` list in `tests/embeddings/evaluate_models.py`.
2.  Execute the **Run Full Evaluation** command.
3.  Note that the final report will only contain the models listed in that specific run.

### Troubleshooting State
- **OOM Errors**: If the 8B model fails with Out of Memory, reduce `batch_size` to 1 in `evaluate_model()` within `tests/embeddings/evaluate_models.py`.
- **Missing Dependencies**: Rebuild the image using Step 1 if `evaluate_models.py` imports new packages.

## Model Config Reference
| Model | Param Count | VRAM (Approx) | Notes |
| :--- | :--- | :--- | :--- |
| Qwen/Qwen3-Embedding-8B | 8B | 15.5GB (FP16) | Requires `device_map="auto"` |
| intfloat/multilingual-e5-large | 560M | 2.2GB | Strong cross-lingual alignment |
| intfloat/multilingual-e5-base | 278M | 1.1GB | SentencePiece tokenizer, less fragmentation |
| google/mt5-base | 580M | 2.3GB | Massive multilingual, handles long polysynthetic forms |
| google/mt5-large | 1.2B | 4.8GB | Stronger generalization, fits in 20GB |
| facebook/xglm-564M | 564M | 2.2GB | Trained on low-resource, polysynthetic focus |
| sentence-transformers/LaBSE | 470M | 1.8GB | Baseline for low-resource |
| Qwen/Qwen3-Embedding-0.6B | 600M | 1.8GB | High morphological sense |

## Models to Avoid for Algic Languages

These models perform poorly on polysynthetic, low-resource languages:

| Model | Why to Avoid |
| :--- | :--- |
| BGE-M3 | English/Chinese-centric; tokenizer destroys Algic morphology. |
| All-MiniLM-L6-v2 | English-only; fails on unseen morphology. |
| BERT-base-uncased variants | WordPiece tokenizer catastrophically fragments Algic forms. |
