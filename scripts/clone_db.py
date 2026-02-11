# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import shutil
from pathlib import Path
import sys

def clone_db():
    """Clone the local developer database to Junie's private database."""
    project_root = Path(__file__).parent.parent
    local_db = project_root / "tmp" / "local_db"
    junie_db = project_root / "tmp" / "junie_db"

    if not local_db.exists():
        print(f"Error: Local database not found at {local_db}")
        sys.exit(1)

    # Ensure junie_db's parent exists
    junie_db.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing junie_db if it exists
    if junie_db.exists():
        print(f"Removing existing Junie database at {junie_db}...")
        shutil.rmtree(junie_db)

    # Clone using shutil.copytree
    print(f"Cloning {local_db} to {junie_db}...")
    try:
        # Ignore socket files which cause errors during copy
        def ignore_sockets(dir, files):
            return [f for f in files if f.startswith(".s.PGSQL.")]
            
        shutil.copytree(local_db, junie_db, ignore=ignore_sockets)
        print("Clone successful.")
    except Exception as e:
        print(f"Error during cloning: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clone_db()
