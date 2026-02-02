# Copyright (c) 2026 Brothertown Language
"""
Test script for local embedding service.

This script verifies that the Docker-based embedding service is running
and can generate embeddings using the BGE-M3 model.

Usage:
    uv run python scripts/test_embeddings.py
"""

import sys
import httpx
import json


def test_embedding_service(url: str = "http://localhost:8080") -> bool:
    """Test the embedding service health and functionality.
    
    Args:
        url: Base URL of the embedding service
        
    Returns:
        True if service is healthy and working, False otherwise
    """
    print(f"Testing embedding service at {url}...")
    
    # Test 1: Health check
    print("\n1. Checking service health...")
    try:
        response = httpx.get(f"{url}/health", timeout=5.0)
        if response.status_code == 200:
            print("   ✓ Service is healthy")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Cannot connect to service: {e}")
        print("\n   Make sure the embedding service is running:")
        print("   docker-compose up -d embeddings")
        return False
    
    # Test 2: Generate embedding
    print("\n2. Testing embedding generation...")
    test_texts = [
        "dog",
        "wompan",  # Algonquian word
        "The quick brown fox jumps over the lazy dog"
    ]
    
    for text in test_texts:
        try:
            response = httpx.post(
                f"{url}/embed",
                json={"inputs": text},
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"   ✗ Failed to generate embedding for '{text}': {response.status_code}")
                print(f"      Response: {response.text}")
                return False
            
            result = response.json()
            
            # Verify embedding structure
            if not isinstance(result, list) or len(result) == 0:
                print(f"   ✗ Invalid response format for '{text}'")
                return False
            
            embedding = result[0]
            if not isinstance(embedding, list):
                print(f"   ✗ Invalid embedding format for '{text}'")
                return False
            
            # BGE-M3 should return 1024 dimensions
            if len(embedding) != 1024:
                print(f"   ✗ Wrong embedding dimensions for '{text}': {len(embedding)} (expected 1024)")
                return False
            
            print(f"   ✓ Generated {len(embedding)}-dimensional embedding for '{text}'")
            
        except Exception as e:
            print(f"   ✗ Error generating embedding for '{text}': {e}")
            return False
    
    # Test 3: Verify embeddings are different for different texts
    print("\n3. Testing embedding uniqueness...")
    try:
        response1 = httpx.post(
            f"{url}/embed",
            json={"inputs": "dog"},
            timeout=30.0
        )
        response2 = httpx.post(
            f"{url}/embed",
            json={"inputs": "cat"},
            timeout=30.0
        )
        
        emb1 = response1.json()[0]
        emb2 = response2.json()[0]
        
        if emb1 == emb2:
            print("   ✗ Different texts produced identical embeddings")
            return False
        
        print("   ✓ Different texts produce different embeddings")
        
    except Exception as e:
        print(f"   ✗ Error testing uniqueness: {e}")
        return False
    
    # Test 4: Verify embeddings are consistent
    print("\n4. Testing embedding consistency...")
    try:
        response1 = httpx.post(
            f"{url}/embed",
            json={"inputs": "test"},
            timeout=30.0
        )
        response2 = httpx.post(
            f"{url}/embed",
            json={"inputs": "test"},
            timeout=30.0
        )
        
        emb1 = response1.json()[0]
        emb2 = response2.json()[0]
        
        if emb1 != emb2:
            print("   ✗ Same text produced different embeddings")
            return False
        
        print("   ✓ Same text produces consistent embeddings")
        
    except Exception as e:
        print(f"   ✗ Error testing consistency: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All tests passed! Embedding service is working correctly.")
    print("="*60)
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test local embedding service")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Base URL of the embedding service (default: http://localhost:8080)"
    )
    
    args = parser.parse_args()
    
    success = test_embedding_service(args.url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
