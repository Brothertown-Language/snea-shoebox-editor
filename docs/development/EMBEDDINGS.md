<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->

# Embedding Service Configuration

This document describes the embedding service configuration for semantic search in the SNEA Shoebox Editor, including setup for production (Cloudflare) and local development/testing environments.

---

## Overview

The SNEA Shoebox Editor uses **Cloudflare Workers AI** with the **`@cf/baai/bge-m3`** embedding model for semantic search capabilities. This model provides:

- **Multilingual support**: Ideal for Algonquian-English code-switching
- **Sparse retrieval**: Superior performance for low-resource languages
- **1024 dimensions**: High-quality vector representations
- **Hybrid search**: Combines semantic and keyword search with weighted scoring

Embeddings are stored in **Cloudflare Vectorize** (vector database) with metadata tracked in the D1 `embeddings` table.

---

## Architecture

### Components

1. **Cloudflare Workers AI**: Generates embeddings via `@cf/baai/bge-m3` model
2. **Cloudflare Vectorize**: Stores and queries vector embeddings
3. **D1 `embeddings` table**: Tracks metadata (vector_id, model_name, record_version, source_tag)
4. **Stale detection**: Compares `record_version` to trigger recalculation when records change

### Data Flow

```
Record Update → Extract MDF tags → Generate embeddings → Store in Vectorize + D1
Search Query → Generate query embedding → Vectorize search → Combine with FTS → Ranked results
```

---

## Production Configuration (Cloudflare)

### 1. Workers AI Binding

Add the Workers AI binding to `wrangler.toml`:

```toml
[ai]
binding = "AI"
```

This binding provides access to Cloudflare's AI models, including `@cf/baai/bge-m3`.

### 2. Vectorize Index

Create a Vectorize index for storing embeddings:

```bash
# Create the index with 1024 dimensions (required for @cf/baai/bge-m3)
wrangler vectorize create snea-embeddings \
  --dimensions=1024 \
  --metric=cosine
```

Add the Vectorize binding to `wrangler.toml`:

```toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "snea-embeddings"
```

### 3. Usage in Worker Code

```python
from cloudflare.workers import Request, Response, Env

async def generate_embedding(env: Env, text: str) -> list[float]:
    """Generate embedding using Cloudflare Workers AI."""
    response = await env.AI.run(
        "@cf/baai/bge-m3",
        {"text": text}
    )
    return response["data"][0]  # 1024-dimensional vector

async def store_embedding(env: Env, vector_id: str, embedding: list[float], metadata: dict):
    """Store embedding in Vectorize."""
    await env.VECTORIZE.insert([{
        "id": vector_id,
        "values": embedding,
        "metadata": metadata
    }])

async def search_embeddings(env: Env, query_embedding: list[float], top_k: int = 10):
    """Search for similar embeddings."""
    results = await env.VECTORIZE.query(
        vector=query_embedding,
        top_k=top_k,
        return_metadata=True
    )
    return results["matches"]
```

---

## Local Development Configuration

### Challenge

Cloudflare Workers AI and Vectorize are **cloud-only services** and cannot be run locally. Local development requires alternative approaches for testing embedding-related functionality.

### Strategy

For local development, use one of the following approaches:

#### Option 1: Docker-Based Local Embedding Service (Recommended)

**This is the source of truth for local development.** Run the same BGE-M3 model locally using Docker with GPU acceleration.

##### Prerequisites

- Docker with GPU support (NVIDIA Container Toolkit)
- NVIDIA GPU with sufficient VRAM (minimum 8GB, 16GB+ recommended)
- The local machine has been verified with: RTX 3090 (24GB VRAM), 20 CPU cores, 62GB RAM

##### Architecture

The embedding service runs as a separate Docker container using **Hugging Face Text Embeddings Inference (TEI)**:

- **Model**: `BAAI/bge-m3` (same as Cloudflare `@cf/baai/bge-m3`)
- **Dimensions**: 1024 (matches production)
- **API**: REST API compatible with OpenAI embeddings format
- **GPU Acceleration**: Automatic CUDA support for NVIDIA GPUs

##### Docker Configuration

The embedding service is defined in `docker-compose.yml`:

```yaml
services:
  embeddings:
    image: ghcr.io/huggingface/text-embeddings-inference:1.5-cuda
    hostname: embeddings
    ports:
      - "8080:80"
    volumes:
      - embedding_models:/data
    environment:
      - MODEL_ID=BAAI/bge-m3
      - MAX_BATCH_TOKENS=16384
      - MAX_CLIENT_BATCH_SIZE=32
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:80/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: --model-id BAAI/bge-m3 --port 80

volumes:
  embedding_models:
```

##### Usage in Backend Code

The backend automatically detects the local embedding service:

```python
# src/backend/embedding_service.py
import os
import httpx
from typing import List

async def generate_embedding(text: str, env=None) -> List[float]:
    """Generate embedding using appropriate service based on environment."""
    
    # Production: Use Cloudflare Workers AI binding
    if env and hasattr(env, 'AI'):
        response = await env.AI.run("@cf/baai/bge-m3", {"text": text})
        return response["data"][0]
    
    # Local development: Use Docker embedding service
    embedding_url = os.getenv("EMBEDDING_SERVICE_URL", "http://embeddings:80")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{embedding_url}/embed",
            json={"inputs": text}
        )
        # TEI returns embeddings in different format than Cloudflare
        result = response.json()
        return result[0]  # First embedding from batch
```

##### Environment Variables

Add to `.env` file:

```env
# Local embedding service (Docker)
EMBEDDING_SERVICE_URL=http://embeddings:80

# Enable local embeddings in development
USE_LOCAL_EMBEDDINGS=true
```

##### Starting the Service

```bash
# Start all services including embeddings
docker-compose up --build

# Check embedding service health
curl http://localhost:8080/health

# Test embedding generation
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test text"}'
```

##### First Run Notes

- **Model Download**: On first start, the container downloads the BGE-M3 model (~2GB)
- **Startup Time**: Initial startup takes 2-5 minutes for model loading
- **Disk Space**: Requires ~5GB for model and cache
- **Memory**: Model uses ~4GB VRAM when loaded

##### Advantages

- **Production Parity**: Uses the exact same model as Cloudflare
- **Real Embeddings**: Generate actual embeddings for integration testing
- **GPU Acceleration**: Fast inference with CUDA support
- **Offline Development**: No internet required after initial model download
- **Consistent Results**: Embeddings match production behavior

#### Option 2: Mock Embeddings (Unit Tests Only)

Create mock implementations that return deterministic vectors for testing:

```python
# tests/mocks/embedding_service.py
import hashlib
from typing import List

class MockEmbeddingService:
    """Mock embedding service for local testing."""
    
    def __init__(self, dimensions: int = 1024):
        self.dimensions = dimensions
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding based on text hash."""
        # Use hash to create deterministic but varied vectors
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to normalized vector
        vector = []
        for i in range(self.dimensions):
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 255.0) * 2 - 1  # Normalize to [-1, 1]
            vector.append(value)
        
        # Normalize to unit vector (cosine similarity compatible)
        magnitude = sum(v**2 for v in vector) ** 0.5
        return [v / magnitude for v in vector]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        return dot_product  # Already normalized

class MockVectorStore:
    """Mock vector store for local testing."""
    
    def __init__(self):
        self.vectors = {}  # vector_id -> (embedding, metadata)
    
    def insert(self, vector_id: str, embedding: List[float], metadata: dict):
        """Store vector with metadata."""
        self.vectors[vector_id] = (embedding, metadata)
    
    def query(self, query_embedding: List[float], top_k: int = 10):
        """Find most similar vectors."""
        results = []
        for vector_id, (embedding, metadata) in self.vectors.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append({
                "id": vector_id,
                "score": similarity,
                "metadata": metadata
            })
        
        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        return sum(a * b for a, b in zip(vec1, vec2))
```

Usage in tests:

```python
# tests/test_embeddings.py
import unittest
from tests.mocks.embedding_service import MockEmbeddingService, MockVectorStore

class TestEmbeddings(unittest.TestCase):
    def setUp(self):
        self.embedding_service = MockEmbeddingService()
        self.vector_store = MockVectorStore()
    
    def test_similar_texts_have_similar_embeddings(self):
        """Test that similar texts produce similar embeddings."""
        text1 = "dog"
        text2 = "dog"
        text3 = "completely different text"
        
        emb1 = self.embedding_service.generate_embedding(text1)
        emb2 = self.embedding_service.generate_embedding(text2)
        emb3 = self.embedding_service.generate_embedding(text3)
        
        # Identical texts should have identical embeddings
        self.assertEqual(emb1, emb2)
        
        # Different texts should have different embeddings
        self.assertNotEqual(emb1, emb3)
```

**Use Case**: Fast unit tests that don't require real embeddings. Mock embeddings are deterministic and require no external services.

#### Option 3: Remote Development Environment (Fallback)

For situations where local Docker embedding service cannot be used (e.g., no GPU, limited resources):

1. **Use Cloudflare Workers in dev mode**: Deploy to a development worker that has AI and Vectorize bindings
2. **Environment variable**: Set `CLOUDFLARE_DEV_MODE=true` to route embedding requests to the dev worker
3. **API proxy**: Local worker proxies embedding requests to the remote dev worker

```python
# src/backend/embedding_service.py
import os
import httpx
from typing import List

async def generate_embedding(text: str, env=None) -> List[float]:
    """Generate embedding using appropriate service based on environment."""
    
    # Production: Use Cloudflare Workers AI binding
    if env and hasattr(env, 'AI'):
        response = await env.AI.run("@cf/baai/bge-m3", {"text": text})
        return response["data"][0]
    
    # Local development: Use Docker embedding service (Option 1)
    if os.getenv("USE_LOCAL_EMBEDDINGS") == "true":
        embedding_url = os.getenv("EMBEDDING_SERVICE_URL", "http://embeddings:80")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{embedding_url}/embed",
                json={"inputs": text}
            )
            result = response.json()
            return result[0]
    
    # Remote dev worker (Option 3)
    if os.getenv("CLOUDFLARE_DEV_MODE") == "true":
        dev_url = os.getenv("CLOUDFLARE_DEV_WORKER_URL")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{dev_url}/api/embeddings/generate",
                json={"text": text}
            )
            return response.json()["embedding"]
    
    # Fallback: Mock for unit tests (Option 2)
    from tests.mocks.embedding_service import MockEmbeddingService
    mock_service = MockEmbeddingService()
    return mock_service.generate_embedding(text)
```

**Use Case**: Integration testing when local GPU resources are unavailable. Requires internet connection and deployed dev worker.

---

## Local Testing Strategy

### Unit Tests

Use **Option 2 (Mock Embeddings)** for all unit tests:

- Fast execution (no network calls)
- Deterministic results (reproducible tests)
- No external dependencies
- Tests focus on logic, not embedding quality

```bash
# Run unit tests with mocks (no Docker required)
uv run python -m unittest discover tests
```

### Integration Tests

For integration tests that require real embeddings, use **Option 1 (Docker-Based Local Embedding Service)**:

1. **Start embedding service**: `docker-compose up embeddings`
2. **Set environment variables**: `USE_LOCAL_EMBEDDINGS=true`
3. **Run integration tests**: Tests will use real BGE-M3 embeddings

```bash
# Start embedding service
docker-compose up -d embeddings

# Wait for service to be ready
curl --retry 10 --retry-delay 5 http://localhost:8080/health

# Run integration tests with real embeddings
USE_LOCAL_EMBEDDINGS=true uv run python -m unittest discover tests/integration
```

### Manual Testing

For manual testing and development:

1. **Use Option 1 (Docker Embeddings)** as the default
2. **Enable in .env**: Set `USE_LOCAL_EMBEDDINGS=true`
3. **Fallback to Option 3**: Use remote dev worker if Docker is unavailable

```python
import unittest
import os

class TestEmbeddingIntegration(unittest.TestCase):
    @unittest.skipUnless(
        os.getenv("ENABLE_INTEGRATION_TESTS") == "true",
        "Integration tests disabled (set ENABLE_INTEGRATION_TESTS=true)"
    )
    def test_real_embedding_generation(self):
        """Test with real Cloudflare Workers AI."""
        # This test only runs when explicitly enabled
        pass
```

### Manual Testing

For manual testing of embedding features during local development:

1. **Deploy to dev worker**: `wrangler deploy --env dev`
2. **Test via dev URL**: Use the dev worker URL for manual testing
3. **Inspect results**: Check D1 and Vectorize via Cloudflare dashboard

---

## Environment Variables

### Production (.env not needed)

Production uses Cloudflare bindings configured in `wrangler.toml`. No environment variables required.

### Local Development (.env)

```env
# Optional: Enable integration tests with real embeddings
ENABLE_INTEGRATION_TESTS=false

# Optional: Remote dev worker for integration testing
CLOUDFLARE_DEV_MODE=false
CLOUDFLARE_DEV_WORKER_URL=https://snea-editor-dev.your-subdomain.workers.dev
```

---

## Embedding Generation Strategy

### When to Generate Embeddings

Embeddings are generated for the following MDF tags:

1. **`\lx`** (Lexeme): Primary headword
2. **`\ge`** (Gloss): English translation
3. **`\va`** (Variant): Lexeme variants
4. **`\nt`** (Note): Linguistic notes
5. **`\xv`** (Example): Example sentences (all languages)

### Embedding Context

To improve search quality, embeddings include contextual information:

```python
def create_embedding_text(record: dict, tag: str, value: str) -> str:
    """Create contextualized text for embedding."""
    
    # Base text
    text = value
    
    # Add context based on tag type
    if tag == "ge":
        # Include lexeme for gloss context
        text = f"{record['lx']}: {value}"
    elif tag == "va":
        # Include main lexeme for variant context
        text = f"{record['lx']} (variant: {value})"
    elif tag == "xv":
        # Include lexeme for example context
        text = f"{record['lx']} - {value}"
    
    return text
```

### Stale Detection and Recalculation

The `embeddings` table tracks `record_version` to detect when embeddings are stale:

```python
async def check_embeddings_stale(db, record_id: int, current_version: int) -> bool:
    """Check if embeddings need recalculation."""
    result = await db.execute(
        "SELECT COUNT(*) as count FROM embeddings WHERE record_id = ? AND record_version != ?",
        [record_id, current_version]
    )
    return result["count"] > 0

async def recalculate_embeddings(env, record: dict):
    """Recalculate embeddings for a record."""
    # Extract tags that need embeddings
    tags_to_embed = extract_embeddable_tags(record["mdf_data"])
    
    # Generate and store new embeddings
    for tag, value in tags_to_embed:
        embedding_text = create_embedding_text(record, tag, value)
        embedding = await generate_embedding(env, embedding_text)
        vector_id = str(uuid.uuid4())
        
        # Store in Vectorize
        await env.VECTORIZE.insert([{
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "record_id": record["id"],
                "source_tag": tag,
                "record_version": record["current_version"]
            }
        }])
        
        # Store metadata in D1
        await env.DB.execute(
            """INSERT INTO embeddings 
               (record_id, vector_id, source_tag, original_text, embedded_text, 
                model_name, record_version)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [record["id"], vector_id, tag, value, embedding_text,
             "@cf/baai/bge-m3", record["current_version"]]
        )
```

---

## Hybrid Search Implementation

Combine semantic (vector) and keyword (FTS) search with weighted scoring:

```python
async def hybrid_search(env, query: str, weights: dict = None):
    """Perform hybrid search combining semantic and keyword search."""
    
    if weights is None:
        weights = {"semantic": 0.6, "keyword": 0.4}
    
    # Generate query embedding
    query_embedding = await generate_embedding(env, query)
    
    # Semantic search via Vectorize
    vector_results = await env.VECTORIZE.query(
        vector=query_embedding,
        top_k=50,
        return_metadata=True
    )
    
    # Keyword search via FTS
    fts_results = await env.DB.execute(
        """SELECT records.id, records.lx, records.ge, 
                  rank as fts_score
           FROM records_fts
           JOIN records ON records.id = records_fts.rowid
           WHERE records_fts MATCH ?
           ORDER BY rank
           LIMIT 50""",
        [query]
    )
    
    # Combine and score
    combined_scores = {}
    
    # Add semantic scores
    for match in vector_results["matches"]:
        record_id = match["metadata"]["record_id"]
        combined_scores[record_id] = {
            "semantic": match["score"] * weights["semantic"],
            "keyword": 0
        }
    
    # Add keyword scores (normalize FTS rank to 0-1 range)
    max_fts_score = max([r["fts_score"] for r in fts_results], default=1)
    for result in fts_results:
        record_id = result["id"]
        normalized_fts = result["fts_score"] / max_fts_score
        
        if record_id in combined_scores:
            combined_scores[record_id]["keyword"] = normalized_fts * weights["keyword"]
        else:
            combined_scores[record_id] = {
                "semantic": 0,
                "keyword": normalized_fts * weights["keyword"]
            }
    
    # Calculate final scores and sort
    final_results = []
    for record_id, scores in combined_scores.items():
        final_score = scores["semantic"] + scores["keyword"]
        final_results.append({
            "record_id": record_id,
            "score": final_score,
            "semantic_score": scores["semantic"],
            "keyword_score": scores["keyword"]
        })
    
    final_results.sort(key=lambda x: x["score"], reverse=True)
    return final_results[:20]  # Return top 20
```

---

## Troubleshooting

### Production Issues

**Problem**: Embeddings not generating
- **Check**: Verify AI binding in `wrangler.toml`
- **Check**: Confirm Workers AI is enabled for your account
- **Check**: Review worker logs for errors

**Problem**: Vector search returns no results
- **Check**: Verify Vectorize index exists: `wrangler vectorize list`
- **Check**: Confirm embeddings are being inserted (check D1 `embeddings` table)
- **Check**: Verify dimensions match (1024 for `@cf/baai/bge-m3`)

### Local Development Issues

**Problem**: Tests fail with "AI binding not found"
- **Solution**: Ensure tests use mock embeddings (Option 1)
- **Check**: Verify mock imports in test files

**Problem**: Integration tests timeout
- **Solution**: Check `CLOUDFLARE_DEV_WORKER_URL` is set correctly
- **Solution**: Verify dev worker is deployed and accessible

---

## Cost Considerations

### Cloudflare Workers AI

- **Free tier**: 10,000 neurons per day (sufficient for development)
- **Paid tier**: $0.011 per 1,000 neurons
- **Neuron calculation**: Each embedding request uses neurons based on input tokens

### Cloudflare Vectorize

- **Free tier**: 5 million queried vector dimensions per month
- **Paid tier**: $0.04 per 1 million queried vector dimensions
- **Storage**: Included in Workers paid plan

### Optimization Tips

1. **Batch processing**: Generate embeddings in batches during off-peak hours
2. **Selective embedding**: Only embed essential tags (skip redundant data)
3. **Cache query embeddings**: Cache common query embeddings to reduce AI calls
4. **Lazy recalculation**: Only recalculate embeddings when search detects staleness

---

## Future Enhancements

1. **Multi-model support**: Allow switching between embedding models
2. **Embedding versioning**: Track model versions for migration
3. **Batch recalculation**: Background job for bulk embedding updates
4. **Quality metrics**: Track search relevance and embedding quality
5. **A/B testing**: Compare different embedding strategies and weights
