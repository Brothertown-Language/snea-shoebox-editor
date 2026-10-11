# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import sys
from pathlib import Path

import pytest

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Isolation via the `private_db` fixture (tests/conftest.py) — see #1426:
# the historic in-test `os.environ["OPENCODE"] = "1"` relied on the import-time
# leak from other modules; the fixture scopes the private scratch DB to this
# module instead of redirecting the whole session.
pytestmark = pytest.mark.usefixtures("private_db")

from src.database.connection import get_session, init_db
from src.database.models.iso639 import ISO639_3


def test_iso639_seeding():
    print("Starting ISO 639-3 seeding test...")

    # The `private_db` fixture provides the isolated private scratch database.

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
            sample = session.query(ISO639_3).filter_by(id="eng").first()
            if sample:
                print(f"Sample 'eng': {sample.ref_name}")
            else:
                print("WARNING: 'eng' not found in seeded data.")

            # Test idempotency
            print("Testing idempotency...")
            from src.database.migrations import MigrationManager

            MigrationManager(engine).seed_iso_639_data()
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
