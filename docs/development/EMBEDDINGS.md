<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->

# [FUTURE FEATURE] Embedding Service Configuration

### [DEFERRED / FUTURE FEATURE]
Semantic search and Hugging Face integration are **NOT currently implemented** in the production application. This feature is deferred indefinitely due to budget constraints regarding dedicated inference hosting and API costs.

### [STATIC CROSS-LINKING GOAL]
The long-term goal for embeddings in the SNEA Shoebox Editor is to provide **static cross-linked semantic relationships** for linguist use (browsing and researching relationships between lemmas and glosses). 

Importantly, this approach:
- **Does NOT require live embedding** on the live site.
- **Does NOT require keeping the database up-to-date for live vector searching**.

Instead, embeddings will be used to generate static discovery aids that can be referenced by the editor without real-time AI inference.

The documentation below remains for future research and implementation reference for when those static relationships are being built.

## Overview

The SNEA Shoebox Editor is designed to support semantic search using **pgvector** on **Aiven (PostgreSQL)**.

- **Vector Database**: pgvector extension.
- **Model Selection**:
    - **Best free-tier model (Default)**: `intfloat/multilingual-e5-small`. Selected for strong multilingual performance, support for low-resource languages, and compatibility with the Hugging Face free-tier serverless Inference API. (384 dimensions)
    - **Best overall model (if local GPU)**: `intfloat/multilingual-e5-large`. (1024 dimensions)
    - **Best research-grade model**: `google/mt5-base` (mean-pooled encoder embeddings). (768 dimensions)
- **Dimensions**: 384 dimensions (for the default e5-small model).

## Architecture

1. **Embedding Generation**: Text from MDF tags (\lx, \ge, etc.) is sent to an embedding model.
2. **Storage**: The resulting 384-dimensional vector is stored in the `embeddings` table in PostgreSQL using the `VECTOR` type.
3. **Search**: Queries are converted to embeddings and matched using cosine similarity in SQL.

```sql
-- Cosine distance in pgvector
SELECT * FROM embeddings
ORDER BY embedding <=> '[query_vector]'
LIMIT 10;
```

## Lifecycle and Regeneration

Embeddings must stay in sync with the record data. The following logic is used to manage their lifecycle:

### 1. Initial Generation
When a new record is created, embeddings are generated for the following MDF tags:
- `\lx` (Lexeme)
- `\ge` (English Gloss)
- `\va` (Variant)

### 2. Automatic Regeneration
Embeddings are regenerated whenever a record is updated.
- **Version Tracking**: The `embeddings` table stores the `record_version` for which it was generated.
- **Mismatch Detection**: If `records.current_version > embeddings.record_version`, the embeddings are considered stale.
- **Update Trigger**: The application checks for stale embeddings on record save or during a background synchronization process.

### 3. Deletion
When a record is soft-deleted (`is_deleted = 1`), its associated embeddings are typically ignored in search results. If a record is hard-deleted, embeddings are removed via `ON DELETE CASCADE`.

## Embedding Service (Hugging Face Inference API)

To maintain a "no-charge-ever" stack and ensure perfect parity between environments, we use the **Hugging Face Inference API (Serverless)** exclusively. This service is free to use with a standard Hugging Face account and supports the `BAAI/bge-m3` model.

### 1. Setup Instructions

1.  **Create a Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co/join).
2.  **Generate an Access Token**:
    - Go to **Settings > Access Tokens**.
    - Click **New token**.
    - Select **Classic** (type) and the **Read** role.
3.  **Configure Secrets**:
    - **Production**: Add these to your Streamlit Cloud "Secrets" UI.
    - **Local Development**: Add these to `.streamlit/secrets.toml` (recommended for Streamlit) OR `.env` for standalone scripts.

```toml
[embedding]
model_id = "intfloat/multilingual-e5-small"
api_key = "hf_your_token_here"
```

### 2. Implementation

The application uses the official `huggingface_hub` library to interact with the Hugging Face API.

```python
from huggingface_hub import InferenceClient
import streamlit as st

async def generate_embedding(text: str) -> list[float]:
    """Generates a 384-dimensional embedding using Hugging Face Inference API."""
    client = InferenceClient(
        model=st.secrets["embedding"]["model_id"],
        token=st.secrets["embedding"]["api_key"]
    )
    # The Inference API returns a list of floats for feature-extraction
    return client.feature_extraction(text)
```

## Environment Parity

Both local development and production MUST use the same Hugging Face model via the official library. This ensures that vector matches are consistent across all environments without the need for local model hosting.

### Models to Avoid for Algic Languages

The following models perform poorly on polysynthetic, low-resource languages and should not be used:
- **BGE-M3**: English/Chinese-centric; tokenizer destroys Algic morphology.
- **All-MiniLM-L6-v2**: English-only; fails on unseen morphology.
- **BERT-base-uncased variants**: WordPiece tokenizer catastrophically fragments Algic forms.
