# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_connection():
    # Load .env file
    load_dotenv()
    
    db_url = os.getenv("AIVEN_URI") or os.getenv("DATABASE_URL")
    
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if not db_url:
        print("Error: AIVEN_URI or DATABASE_URL not found in .env")
        sys.exit(1)
        
    print(f"Attempting to connect to database...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Successfully connected!")
            print(f"PostgreSQL version: {version}")
            
            # Check if it's Aiven (usually contains 'aiven' in the version string or we can check the host)
            if "aiven" in db_url.lower():
                print("Verified: Connection is to Aiven host.")
            
            return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("Test passed.")
        sys.exit(0)
    else:
        print("Test failed.")
        sys.exit(1)
