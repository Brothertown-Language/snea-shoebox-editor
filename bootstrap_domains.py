# ============================================================
# === BEGIN SECTION: Imports and Environment Setup ============
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# === END SECTION: Imports and Environment Setup =============
# ============================================================



# ============================================================
# === BEGIN SECTION: Configuration Constants =================
# ============================================================

BACKEND_NAME = os.getenv("BACKEND_NAME", "snea-backend")
PAGES_NAME = os.getenv("PAGES_NAME", "snea-shoebox-editor")

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
    if CF_EMAIL and CF_KEY:
        return {
            "X-Auth-Email": CF_EMAIL,
            "X-Auth-Key": CF_KEY,
            "Content-Type": "application/json",
        }
    elif CF_TOKEN:
        return {
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        }
    else:
        raise Exception("Missing Cloudflare credentials.")


def cf_get(url):
    return requests.get(url, headers=cf_headers())


def cf_post(url, json):
    return requests.post(url, headers=cf_headers(), json=json)

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

    worker_domain_payload = {
        "hostname": BACKEND_DOMAIN,
        "service": BACKEND_NAME,
        "environment": "production",
    }

    r = cf_post(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/domains",
        json=worker_domain_payload,
    )
