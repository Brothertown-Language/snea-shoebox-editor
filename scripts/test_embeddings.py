# Copyright (c) 2026 Brothertown Language
"""
Test script for Hugging Face Inference API embedding service.

This script verifies that the configured Hugging Face Inference API
can generate embeddings using the multilingual-e5-small model.

Usage:
    uv run python scripts/test_embeddings.py
"""

import sys
import os
from typing import Optional
from huggingface_hub import InferenceClient


def test_embedding_service(model_id: str, api_key: Optional[str] = None) -> bool:
    """Test the embedding service health and functionality.
    
    Args:
        model_id: Model ID of the Hugging Face model
        api_key: Optional API key for authentication
        
    Returns:
        True if service is working, False otherwise
    """
    print(f"Testing embedding service with model {model_id}...")
    
    client = InferenceClient(model=model_id, token=api_key, timeout=30)
    
    # Test 0: Health Check (Check if model is accessible)
    print("\n0. Performing health check...")
    try:
        from huggingface_hub import model_info
        info = model_info(model_id, token=api_key)
        print(f"   Model ID: {info.modelId}")
        print(f"   Tags: {info.tags}")
    except Exception as e:
        print(f"   ! Health check (model_info) failed: {e}")

    # Test 1: Generate embedding
    print("\n1. Testing embedding generation (feature_extraction)...")
    test_texts = [
        "dog",
        "wompan",  # Algonquian word
        "The quick brown fox jumps over the lazy dog"
    ]
    
    for text in test_texts:
        try:
            print(f"   Requesting embedding for '{text}'...")
            # feature_extraction is the correct high-level method in InferenceClient
            # for getting embeddings.
            embedding = client.feature_extraction(text)
            
            # multilingual-e5-small should return 384 dimensions
            if len(embedding) != 384:
                print(f"   ✗ Wrong embedding dimensions for '{text}': {len(embedding)} (expected 384)")
                return False
            
            print(f"   ✓ Generated {len(embedding)}-dimensional embedding for '{text}'")
            
        except Exception as e:
            print(f"   ✗ Error generating embedding for '{text}': {e}")
            if "401" in str(e):
                print("      TIP: Check your Hugging Face API token.")
            return False
    
    print("\n" + "="*60)
    print("✓ All tests passed! Embedding service is working correctly.")
    print("="*60)
    return True


def main():
    """Main entry point."""
    import argparse
    
    # Default to the value in secrets if possible, otherwise use the standard model ID
    default_model = "intfloat/multilingual-e5-small"
    default_key = None
    
    # Try to load from .streamlit/secrets.toml if it exists
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        try:
            import tomllib
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
                if "embedding" in secrets:
                    default_model = secrets["embedding"].get("model_id", default_model)
                    default_key = secrets["embedding"].get("api_key", default_key)
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Test Hugging Face embedding service")
    parser.add_argument(
        "--model",
        default=default_model,
        help=f"Model ID of the embedding service (default: {default_model})"
    )
    parser.add_argument(
        "--key",
        default=default_key,
        help="Hugging Face API key (token)"
    )
    
    args = parser.parse_args()
    
    if not args.key:
        print("WARNING: No API key provided. Requests may be rate-limited or fail.")
    
    success = test_embedding_service(args.model, args.key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
