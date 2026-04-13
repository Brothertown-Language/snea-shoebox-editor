# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import shutil
from pathlib import Path
import sys


def clone_db():
    """Clone the local developer database to the OpenCode private database."""
    project_root = Path(__file__).parent.parent
    local_db = project_root / "tmp" / "local_db"
    opencode_db = project_root / "tmp" / "opencode_db"

    if not local_db.exists():
        print(f"Error: Local database not found at {local_db}")
        sys.exit(1)

    opencode_db.parent.mkdir(parents=True, exist_ok=True)

    if opencode_db.exists():
        print(f"Removing existing OpenCode database at {opencode_db}...")
        shutil.rmtree(opencode_db)

    print(f"Cloning {local_db} to {opencode_db}...")
    try:

        def ignore_sockets(dir, files):
            return [f for f in files if f.startswith(".s.PGSQL.")]

        shutil.copytree(local_db, opencode_db, ignore=ignore_sockets)
        print("Clone successful.")
    except Exception as e:
        print(f"Error during cloning: {e}")
        sys.exit(1)


if __name__ == "__main__":
    clone_db()
