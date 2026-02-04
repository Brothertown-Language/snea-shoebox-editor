# Copyright (c) 2026 Brothertown Language
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.database import get_db_url, is_production

def test_db_resolution():
    # Detect environment
    is_prod = is_production()
    url = get_db_url()
    
    print(f"Is Production: {is_prod}")
    print(f"Resolved DB URL: {url}")
    
    if is_prod:
        print("Verification: Running in simulated production.")
    else:
        print("Verification: Running in local development.")
        if "local_db" in url or "127.0.0.1" in url or "localhost" in url:
            print("SUCCESS: Local database (pgserver or localhost) resolved.")
        else:
            print("FAILURE: Production database resolved in local environment.")

if __name__ == "__main__":
    test_db_resolution()
