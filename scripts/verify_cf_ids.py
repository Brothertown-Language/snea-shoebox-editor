# Copyright (c) 2026 Brothertown Language
import os
import sys
from cloudflare import Cloudflare
from dotenv import load_dotenv

def verify_cloudflare_ids():
    """
    Queries Cloudflare API to verify if the account ID and service name are valid.
    Fails early if any ID is invalid.
    """
    load_dotenv()
    
    cf_token = os.getenv("CLOUDFLARE_API_TOKEN") or os.getenv("PROD_CF_API_TOKEN")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    
    # In CI, we expect these to be set via environment variables
    if not cf_token:
        print("ERROR: CLOUDFLARE_API_TOKEN is not set.")
        sys.exit(1)
    
    if not account_id:
        print("ERROR: CLOUDFLARE_ACCOUNT_ID is not set.")
        sys.exit(1)

    print(f"Verifying Cloudflare Account ID: {account_id}")
    cf = Cloudflare(api_token=cf_token)

    try:
        # 1. Verify Account Access
        account = cf.accounts.get(account_id=account_id)
        print(f"SUCCESS: Access verified for account '{account.name}' ({account.id})")
        
        # 2. Verify D1 database from wrangler.toml
        # We parse wrangler.toml to get the database name/id
        db_name = None
        db_id = None
        if os.path.exists("wrangler.toml"):
            with open("wrangler.toml", "r") as f:
                for line in f:
                    if "database_name" in line:
                        db_name = line.split("=")[1].strip().replace('"', '')
                    if "database_id" in line:
                        db_id = line.split("=")[1].strip().replace('"', '')
        
        if db_id:
            print(f"Verifying D1 Database ID: {db_id}")
            try:
                db = cf.d1.database.get(database_id=db_id, account_id=account_id)
                print(f"SUCCESS: D1 Database '{db.name}' verified.")
            except Exception as e:
                print(f"ERROR: D1 Database ID '{db_id}' not found or inaccessible: {e}")
                sys.exit(1)
        else:
            print("WARNING: No D1 database ID found in wrangler.toml to verify.")

    except Exception as e:
        print(f"ERROR: Cloudflare API verification failed: {e}")
        # If we get a 7003 or similar, it will be caught here
        sys.exit(1)

    print("All Cloudflare IDs verified successfully.")

if __name__ == "__main__":
    verify_cloudflare_ids()
