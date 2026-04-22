#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""GitBucket API Deficiencies Test Suite.

Tests the documented API deficiencies to verify if they persist after GitBucket upgrades.
This should be run after any GitBucket version change to verify API behavior.

Test Coverage:
  - Deficiency #1: PATCH /issues/:number (returns 404)
  - Deficiency #2: add_labels_to_issue (returns empty array, labels NOT added)
  - Deficiency #3: replace_issue_labels (returns empty array, labels NOT set)

Usage:
    ./.opencode/skills/issue-operations/platforms/gitbucket-api/tests/test_api_deficiencies.py

Requirements:
    - .env file with GITBUCKET_URL and GITBUCKET_TOKEN
    - Network access to GitBucket server

Expected Results:
    - All deficiencies should show as BROKEN on current GitBucket v4.42.1
    - Document any changes in API-DEFICIENCIES.md after running
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GITBUCKET_URL = (os.environ.get("GITBUCKET_HTML_URL") or os.environ.get("GITBUCKET_URL", "")).rstrip("/")
GITBUCKET_TOKEN = os.environ.get("GITBUCKET_TOKEN", "")

if not GITBUCKET_URL or not GITBUCKET_TOKEN:
    print("ERROR: GITBUCKET_HTML_URL (or GITBUCKET_URL) and GITBUCKET_TOKEN required in .env")
    sys.exit(1)

API_BASE = f"{GITBUCKET_URL}/api/v3"
HEADERS = {
    "Authorization": f"token {GITBUCKET_TOKEN}",
    "Content-Type": "application/json",
}

# Test repository
OWNER = os.environ.get("GIT_OWNER", "<GitOwner>")
REPO = "ai-agent-testing"


def test_patch_issue():
    """Test deficiency #1: PATCH /issues/:number returns 404."""
    print("\n=== Deficiency #1: PATCH /issues/:number ===")

    # First create a test issue
    create_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues"
    create_data = {"title": "API Test Issue", "body": "Testing PATCH operation"}

    try:
        create_resp = requests.post(create_url, headers=HEADERS, json=create_data, timeout=10)
        if create_resp.status_code not in [200, 201]:
            print(f"⚠️  Failed to create test issue: {create_resp.status_code}")
            print(f"   Response: {create_resp.text[:200]}")
            return False

        issue = create_resp.json()
        issue_number = issue["number"]
        print(f"✅ Created test issue #{issue_number}")

        # Now try to PATCH it
        patch_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}"
        patch_data = {
            "title": "Updated Title",
            "body": "Updated body",
            "state": "closed",
        }

        print(f"Testing PATCH {patch_url}")
        patch_resp = requests.patch(patch_url, headers=HEADERS, json=patch_data, timeout=10)

        print(f"   Status: {patch_resp.status_code}")
        print(f"   Response: {patch_resp.text[:200]}")

        if patch_resp.status_code == 200:
            print("✅ PATCH /issues/:number NOW WORKS!")
            # Verify the update
            get_resp = requests.get(patch_url, headers=HEADERS, timeout=10)
            if get_resp.status_code == 200:
                updated = get_resp.json()
                print(f"   Title: {updated['title']}")
                print(f"   State: {updated['state']}")
            return True
        elif patch_resp.status_code == 404:
            print("❌ PATCH /issues/:number still returns 404")
            print("   GitBucket does NOT support issue updates via API")
            return False
        else:
            print(f"⚠️  Unexpected status: {patch_resp.status_code}")
            return False

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def test_add_labels(issue_number=None):
    """Test deficiency #2: add_labels_to_issue returns empty array."""
    print("\n=== Deficiency #2: Add Labels Returns Empty Array ===")

    if issue_number is None:
        # Create a test issue
        create_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues"
        create_data = {"title": "Label Test Issue", "body": "Testing label operations"}

        try:
            create_resp = requests.post(create_url, headers=HEADERS, json=create_data, timeout=10)
            if create_resp.status_code not in [200, 201]:
                print(f"⚠️  Failed to create test issue: {create_resp.status_code}")
                return False

            issue = create_resp.json()
            issue_number = issue["number"]
            print(f"✅ Created test issue #{issue_number}")
        except requests.RequestException as e:
            print(f"❌ Request error: {e}")
            return False

    # Add labels
    labels_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}/labels"
    labels_data = ["test-label-1", "test-label-2"]

    print(f"Testing POST {labels_url}")
    print(f"   Labels to add: {labels_data}")

    try:
        add_resp = requests.post(labels_url, headers=HEADERS, json=labels_data, timeout=10)

        print(f"   Status: {add_resp.status_code}")
        print(f"   Response: {add_resp.text[:200]}")

        if add_resp.status_code == 200:
            result = add_resp.json()
            print(f"   Response type: {type(result)}")
            print(f"   Response length: {len(result)}")

            if isinstance(result, list) and len(result) == 0:
                print("⚠️  Returns empty array (deficiency still present)")
            elif isinstance(result, list) and len(result) > 0:
                print("✅ Returns array of labels!")
                print(f"   Labels: {[l.get('name') for l in result]}")
            else:
                print(f"⚠️  Unexpected response: {result}")

            # Verify labels were actually added
            get_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}"
            get_resp = requests.get(get_url, headers=HEADERS, timeout=10)
            if get_resp.status_code == 200:
                issue = get_resp.json()
                actual_labels = issue.get("labels", [])
                print(f"   Issue actually has {len(actual_labels)} labels:")
                for label in actual_labels:
                    print(f"     - {label.get('name')}")

                if len(actual_labels) > 0:
                    print("✅ Labels were added successfully (despite empty response)")
                    return True
                else:
                    print("❌ Labels were NOT added")
                    return False
        else:
            print(f"❌ Failed to add labels: {add_resp.status_code}")
            return False

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def test_replace_labels(issue_number=None):
    """Test if replace_issue_labels works as workaround."""
    print("\n=== Testing replace_issue_labels Workaround ===")

    if issue_number is None:
        # Create a test issue
        create_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues"
        create_data = {
            "title": "Replace Labels Test",
            "body": "Testing replace operation",
        }

        try:
            create_resp = requests.post(create_url, headers=HEADERS, json=create_data, timeout=10)
            if create_resp.status_code not in [200, 201]:
                print(f"⚠️  Failed to create test issue: {create_resp.status_code}")
                return False

            issue = create_resp.json()
            issue_number = issue["number"]
            print(f"✅ Created test issue #{issue_number}")
        except requests.RequestException as e:
            print(f"❌ Request error: {e}")
            return False

    # Replace labels
    labels_url = f"{API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}/labels"
    labels_data = ["replace-test-1", "replace-test-2"]

    print(f"Testing PUT {labels_url}")
    print(f"   Labels to set: {labels_data}")

    try:
        replace_resp = requests.put(labels_url, headers=HEADERS, json=labels_data, timeout=10)

        print(f"   Status: {replace_resp.status_code}")
        print(f"   Response: {replace_resp.text[:200]}")

        if replace_resp.status_code == 200:
            result = replace_resp.json()
            if isinstance(result, list) and len(result) > 0:
                print("✅ replace_issue_labels WORKS!")
                print(f"   Labels: {[l.get('name') for l in result]}")
                return True
            else:
                print(f"⚠️  Unexpected response: {result}")
                return False
        else:
            print(f"❌ Failed to replace labels: {replace_resp.status_code}")
            return False

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def main():
    print("GitBucket API Deficiencies Test")
    print("=" * 50)
    print(f"API Base: {API_BASE}")
    print(f"Repository: {OWNER}/{REPO}")

    results = {
        "patch_issue": test_patch_issue(),
        "add_labels": test_add_labels(),
        "replace_labels": test_replace_labels(),
    }

    print("\n=== Summary ===")
    for test_name, passed in results.items():
        status = "✅ FIXED" if passed else "❌ BROKEN"
        print(f"{status}: {test_name}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
