# Copyright (c) 2026 Brothertown Language
# ============================================================
# === BEGIN SECTION: Imports and Environment Setup ============
# ============================================================

import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# === END SECTION: Imports and Environment Setup =============
# ============================================================



# ============================================================
# === BEGIN SECTION: Configuration Constants =================
# ============================================================

BACKEND_NAME = os.getenv("BACKEND_NAME", "snea-backend")
PAGES_NAME = os.getenv("PAGES_NAME", "snea-editor")

DOMAIN = os.getenv("DOMAIN", "michael-conrad.com")
BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN", f"snea-backend.{DOMAIN}")
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", f"snea-editor.{DOMAIN}")

CF_EMAIL = os.getenv("PROD_CF_EMAIL")
CF_KEY = os.getenv("PROD_CF_API_KEY")
CF_TOKEN = os.getenv("PROD_CF_API_TOKEN")

# ============================================================
# === END SECTION: Configuration Constants ===================
# ============================================================



# ============================================================
# === BEGIN SECTION: Cloudflare REST Helpers =================
# ============================================================

def cf_headers():
    """
    Returns the correct Cloudflare authentication headers.
    Supports either Global API Key or API Token.
    """
    # If we have a token, we SHOULD use it, but if we have email/key too, 
    # we might want to be careful if the token is 401. 
    # However, this helper is simple. Let's stick to prioritization.
    if CF_TOKEN:
        return {
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        }
    elif CF_EMAIL and CF_KEY:
        return {
            "X-Auth-Email": CF_EMAIL,
            "X-Auth-Key": CF_KEY,
            "Content-Type": "application/json",
        }
    else:
        raise Exception("Missing Cloudflare credentials. Provide PROD_CF_API_TOKEN (Recommended) or PROD_CF_EMAIL and PROD_CF_API_KEY in .env")


def cf_get(url):
    return requests.get(url, headers=cf_headers())


def cf_post(url, json):
    # Some Cloudflare Worker endpoints (like custom domains) strictly forbid 
    # API tokens for POST/PUT if they are scoped tokens, or they might 
    # require Global API Key. 
    
    headers = cf_headers()
    # If using token, and we have global key fallback, try to swap if it's a known problematic endpoint
    if CF_TOKEN and CF_EMAIL and CF_KEY:
        if "/workers/domains" in url:
            print("Switching to Global API Key for Worker domain configuration (Token POST not allowed)...")
            headers = {
                "X-Auth-Email": CF_EMAIL,
                "X-Auth-Key": CF_KEY,
                "Content-Type": "application/json",
            }

    return requests.post(url, headers=headers, json=json)

# ============================================================
# === END SECTION: Cloudflare REST Helpers ===================
# ============================================================



# ============================================================
# === BEGIN SECTION: Main Domain Bootstrap Logic =============
# ============================================================

def bootstrap_domains():
    # --------------------------------------------------------
    # Fetch Account ID
    # --------------------------------------------------------
    print("Fetching Cloudflare account...")

    r = cf_get("https://api.cloudflare.com/client/v4/accounts")
    data = r.json()

    if not data.get("success"):
        raise Exception(f"Failed to fetch accounts: {data}")

    account = data["result"][0]
    account_id = account["id"]

    print(f"Using Cloudflare Account: {account['name']} (ID: {account_id})")

    # --------------------------------------------------------
    # Verify Zone Exists
    # --------------------------------------------------------
    print(f"Verifying zone for domain '{DOMAIN}'...")

    r = cf_get(f"https://api.cloudflare.com/client/v4/zones?name={DOMAIN}")
    data = r.json()

    if not data.get("success") or not data["result"]:
        print(f"WARNING: Zone '{DOMAIN}' not found in this account.")
        zone_id = None
    else:
        zone_id = data["result"][0]["id"]
        print(f"SUCCESS: Zone '{DOMAIN}' found (ID: {zone_id}).")

    # --------------------------------------------------------
    # Worker Custom Domain (REST API)
    # --------------------------------------------------------
    print(f"Ensuring Custom Domain '{BACKEND_DOMAIN}' for Worker '{BACKEND_NAME}'...")

    # For Worker Custom Domains, the endpoint is:
    # PUT /accounts/:account_identifier/workers/domains
    
    worker_domain_payload = {
        "hostname": BACKEND_DOMAIN,
        "service": BACKEND_NAME,
        # "environment": "production", # Environment might not be explicitly named "production" yet
    }

    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/domains",
        headers=cf_headers(),
        json=worker_domain_payload,
    )
    
    if r.status_code in [200, 201]:
        print(f"SUCCESS: Worker domain '{BACKEND_DOMAIN}' configured.")
    elif "already exists" in r.text.lower():
        print(f"SUCCESS: Worker domain '{BACKEND_DOMAIN}' already exists.")
    elif r.status_code == 404 and "does not exist" in r.text:
        print(f"FAILED: Worker '{BACKEND_NAME}' not found. You must deploy the Worker before configuring a custom domain.")
        print(f"HINT: Run 'npx wrangler deploy' or trigger the GitHub Action deployment first.")
    else:
        print(f"FAILED to configure Worker domain: {r.status_code} {r.text}")

    # --------------------------------------------------------
    # Pages Custom Domain (REST API)
    # --------------------------------------------------------
    print(f"Ensuring Custom Domain '{FRONTEND_DOMAIN}' for Pages project '{PAGES_NAME}'...")

    # DEBUG: List projects
    print("Listing Pages projects to verify name...")
    projects_r = cf_get(f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects")
    actual_pages_name = PAGES_NAME
    if projects_r.status_code == 200:
        projects = projects_r.json().get("result", [])
        project_names = [p['name'] for p in projects]
        print(f"Found Projects: {project_names}")
        if PAGES_NAME not in project_names and project_names:
             # AUTO-DETECT: If only one project exists, use it.
             if len(project_names) == 1:
                 actual_pages_name = project_names[0]
                 print(f"Project '{PAGES_NAME}' not found. Using only existing project: '{actual_pages_name}'")
             # Special case for the name found in logs
             elif "michael-conrad-com" in project_names:
                 actual_pages_name = "michael-conrad-com"
                 print(f"Project '{PAGES_NAME}' not found. Falling back to found project: '{actual_pages_name}'")
    else:
        print(f"Failed to list projects: {projects_r.status_code} {projects_r.text}")

    pages_domain_payload = {
        "name": FRONTEND_DOMAIN,
    }

    r = cf_post(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{actual_pages_name}/domains",
        json=pages_domain_payload,
    )

    if r.status_code in [200, 201]:
        print(f"SUCCESS: Pages domain '{FRONTEND_DOMAIN}' configured.")
    elif "already added" in r.text.lower() or "already exists" in r.text.lower():
        print(f"SUCCESS: Pages domain '{FRONTEND_DOMAIN}' already exists.")
    elif r.status_code == 404:
        print(f"FAILED: Pages project '{actual_pages_name}' not found. You must deploy the Pages project before configuring a custom domain.")
        print(f"HINT: Trigger the GitHub Action deployment first.")
    else:
        print(f"FAILED to configure Pages domain: {r.status_code} {r.text}")

    # --------------------------------------------------------
    # Verification Step
    # --------------------------------------------------------
    print("\n--- Starting Verification ---")
    
    # Verify Worker Domain
    print(f"Verifying Worker domain '{BACKEND_DOMAIN}' status...")
    r = cf_get(f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/domains")
    if r.status_code == 200:
        domains = r.json().get("result", [])
        matched = next((d for d in domains if d["hostname"] == BACKEND_DOMAIN), None)
        if matched:
            print(f"VERIFIED: Worker domain '{BACKEND_DOMAIN}' is present.")
            # Some APIs might provide a state or status field, but presence is the first step.
        else:
            print(f"FAILED: Worker domain '{BACKEND_DOMAIN}' NOT found in account list.")
    else:
        print(f"ERROR: Could not fetch Worker domains for verification: {r.status_code}")

    # Verify Pages Domain
    print(f"Verifying Pages domain '{FRONTEND_DOMAIN}' status...")
    r = cf_get(f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{actual_pages_name}/domains")
    if r.status_code == 200:
        domains = r.json().get("result", [])
        matched = next((d for d in domains if d["name"] == FRONTEND_DOMAIN), None)
        if matched:
            status = matched.get("status", "unknown")
            print(f"VERIFIED: Pages domain '{FRONTEND_DOMAIN}' is present (Status: {status}).")
        else:
            print(f"FAILED: Pages domain '{FRONTEND_DOMAIN}' NOT found in project list.")
    else:
        print(f"ERROR: Could not fetch Pages domains for verification: {r.status_code}")

if __name__ == "__main__":
    try:
        bootstrap_domains()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
