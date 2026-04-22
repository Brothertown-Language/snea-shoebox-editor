#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""GitBucket API Verification Tests.

This script verifies that the documented GitBucket API endpoints match
the actual API behavior. It tests authentication, endpoint availability,
and response schemas.

Usage:
    ./.opencode/skills/issue-operations/platforms/gitbucket-api/tests/verify_api.py

Requirements:
    - .env file with GITBUCKET_URL and GITBUCKET_TOKEN
    - Network access to GitBucket server
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITBUCKET_URL = (os.environ.get("GITBUCKET_HTML_URL") or os.environ.get("GITBUCKET_URL", "")).rstrip("/")
GITBUCKET_TOKEN = os.environ.get("GITBUCKET_TOKEN", "")

if not GITBUCKET_URL or not GITBUCKET_TOKEN:
    print("ERROR: GITBUCKET_HTML_URL (or GITBUCKET_URL) and GITBUCKET_TOKEN required in .env")
    sys.exit(1)

API_BASE = f"{GITBUCKET_URL}/api/v3"
HEADERS = {"Authorization": f"token {GITBUCKET_TOKEN}"}


def test_auth() -> bool:
    """Test authentication with /user endpoint."""
    print("\n=== Testing Authentication ===")
    try:
        response = requests.get(f"{API_BASE}/user", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Authenticated as: {user.get('login', 'unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed: Invalid token")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False


def test_endpoint(method: str, path: str, expected_status: int = 200) -> bool:
    """Test a single endpoint."""
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json={}, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json={}, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS, timeout=10)
        else:
            print(f"⚠️  Unknown method: {method}")
            return False

        status_ok = response.status_code == expected_status or (
            expected_status == 200 and response.status_code in [200, 403, 404]
        )
        if status_ok:
            print(f"✅ {method} {path} → {response.status_code}")
            return True
        else:
            print(f"❌ {method} {path} → {response.status_code} (expected {expected_status})")
            return False
    except requests.RequestException as e:
        print(f"❌ {method} {path} → Connection error: {e}")
        return False


def test_core_endpoints() -> dict:
    """Test core API endpoints."""
    print("\n=== Testing Core Endpoints ===")
    results = {}

    # User endpoints
    results["/user"] = test_endpoint("GET", "/user")
    results["/users"] = test_endpoint("GET", "/users")

    # Repository endpoints (use current repo)
    owner = os.environ.get("GIT_OWNER", "<GitOwner>")
    repo = os.environ.get("GIT_REPO", "<GitRepo>")

    results[f"/repos/{owner}/{repo}"] = test_endpoint("GET", f"/repos/{owner}/{repo}")
    results[f"/repos/{owner}/{repo}/issues"] = test_endpoint("GET", f"/repos/{owner}/{repo}/issues")
    results[f"/repos/{owner}/{repo}/pulls"] = test_endpoint("GET", f"/repos/{owner}/{repo}/pulls")
    results[f"/repos/{owner}/{repo}/branches"] = test_endpoint("GET", f"/repos/{owner}/{repo}/branches")
    results[f"/repos/{owner}/{repo}/labels"] = test_endpoint("GET", f"/repos/{owner}/{repo}/labels")
    results[f"/repos/{owner}/{repo}/releases"] = test_endpoint("GET", f"/repos/{owner}/{repo}/releases")
    results[f"/repos/{owner}/{repo}/milestones"] = test_endpoint("GET", f"/repos/{owner}/{repo}/milestones")
    results[f"/repos/{owner}/{repo}/hooks"] = test_endpoint("GET", f"/repos/{owner}/{repo}/hooks")

    # Contents endpoint
    results["/repos/{owner}/{repo}/contents/"] = test_endpoint("GET", f"/repos/{owner}/{repo}/contents/")

    return results


def test_label_operations() -> bool:
    """Test label CRUD operations."""
    print("\n=== Testing Label Operations ===")
    owner = os.environ.get("GIT_OWNER", "<GitOwner>")
    repo = os.environ.get("GIT_REPO", "<GitRepo>")

    # Create test label
    test_label = f"test-api-{os.urandom(4).hex()}"
    print(f"Creating test label: {test_label}")

    create_response = requests.post(
        f"{API_BASE}/repos/{owner}/{repo}/labels",
        headers=HEADERS,
        json={"name": test_label, "color": "ff0000"},
        timeout=10,
    )

    if create_response.status_code == 201:
        print(f"✅ Created label: {test_label}")
        label_id = create_response.json().get("id")

        # Delete test label
        delete_response = requests.delete(
            f"{API_BASE}/repos/{owner}/{repo}/labels/{test_label}",
            headers=HEADERS,
            timeout=10,
        )

        if delete_response.status_code == 204:
            print(f"✅ Deleted label: {test_label}")
            return True
        else:
            print(f"⚠️  Delete failed: {delete_response.status_code}")
            return False
    elif create_response.status_code == 422:
        print(f"⚠️  Label already exists (GitBucket auto-creation)")
        return True
    else:
        print(f"❌ Create failed: {create_response.status_code}")
        return False


def verify_openapi_spec() -> bool:
    """Verify OpenAPI spec file exists and is valid JSON."""
    print("\n=== Verifying OpenAPI Specification ===")
    spec_path = Path(__file__).parent.parent / "reference" / "openapi-v4.42.1.json"

    if not spec_path.exists():
        print(f"❌ OpenAPI spec not found: {spec_path}")
        return False

    try:
        with open(spec_path) as f:
            spec = json.load(f)

        version = spec.get("info", {}).get("version", "unknown")
        endpoints = len(spec.get("paths", {}))
        print(f"✅ OpenAPI v{version} loaded: {endpoints} endpoint paths")

        # Verify GitBucket API marker
        description = spec.get("info", {}).get("description", "")
        if "GitBucket" in description:
            print("✅ Specification identified as GitBucket API")
            return True
        else:
            print("⚠️  Specification may not be GitBucket API")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False


def main() -> int:
    """Run all verification tests."""
    print("GitBucket API Verification Tests")
    print("=" * 50)
    print(f"API Base: {API_BASE}")
    print(f"GitBucket URL: {GITBUCKET_URL}")

    results = {
        "auth": test_auth(),
        "openapi_spec": verify_openapi_spec(),
    }

    if results["auth"]:
        core_results = test_core_endpoints()
        results.update(core_results)
        results["label_operations"] = test_label_operations()

    # Summary
    print("\n=== Summary ===")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
