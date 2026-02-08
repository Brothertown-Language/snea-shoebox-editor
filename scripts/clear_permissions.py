# Copyright (c) 2026 Brothertown Language
"""
Manual script to clear the permissions table for testing.
Usage: uv run python scripts/clear_permissions.py
"""
import sys
import os
from pathlib import Path

# Ensure we are in the project root
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent
os.chdir(project_root)

# Add project root to sys.path
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.database.connection import get_session
from src.database.models.identity import Permission
from sqlalchemy import text

def clear_permissions():
    """Truncate the permissions table."""
    session = get_session()
    try:
        print("Clearing 'permissions' table...")
        session.query(Permission).delete()
        session.commit()
        print("SUCCESS: Permissions table cleared.")
    except Exception as e:
        session.rollback()
        print(f"ERROR: Failed to clear permissions: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_permissions()
