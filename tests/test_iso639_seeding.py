# Copyright (c) 2026 Brothertown Language
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import init_db, get_session
from src.database.models.iso639 import ISO639_3

def test_iso639_seeding():
    print("Starting ISO 639-3 seeding test...")
    
    # Ensure we are using the private database
    os.environ["JUNIE_PRIVATE_DB"] = "true"
    
    # Initialize the database (this should trigger seeding)
    engine = init_db()
    
    # Verify that the table is seeded
    session = get_session()
    try:
        count = session.query(ISO639_3).count()
        print(f"Total ISO 639-3 records: {count}")
        
        if count > 0:
            print("SUCCESS: ISO 639-3 data seeded.")
            # Check a sample entry
            sample = session.query(ISO639_3).filter_by(id='eng').first()
            if sample:
                print(f"Sample 'eng': {sample.ref_name}")
            else:
                print("WARNING: 'eng' not found in seeded data.")

            # Test idempotency
            print("Testing idempotency...")
            from src.database.connection import seed_iso_639_data
            seed_iso_639_data(engine)
            count_after = session.query(ISO639_3).count()
            print(f"Total ISO 639-3 records after second seeding attempt: {count_after}")
            if count == count_after:
                print("SUCCESS: Seeding is idempotent.")
            else:
                print(f"FAILURE: Seeding is NOT idempotent. Expected {count}, got {count_after}")
                sys.exit(1)
        else:
            print("FAILURE: ISO 639-3 data NOT seeded.")
            sys.exit(1)
            
    finally:
        session.close()

if __name__ == "__main__":
    test_iso639_seeding()
