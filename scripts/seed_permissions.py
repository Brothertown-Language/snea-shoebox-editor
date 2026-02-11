# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Manual script to seed the default permissions table.
Usage: uv run python scripts/seed_permissions.py
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

from src.database.connection import get_session, create_engine, get_db_url
from src.database.models.identity import Permission
from sqlalchemy.orm import sessionmaker

def seed_permissions():
    """Seed default permissions if the table is empty."""
    db_url = get_db_url()
    if not db_url:
        print("ERROR: Database URL not found.")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        count = session.query(Permission).count()
        if count > 0:
            print(f"Table 'permissions' already contains {count} entries. Skipping seeding.")
            return

        print("Seeding default permissions...")
        # Admin role for the proto-SNEA-admin team
        admin_perm = Permission(
            github_org="Brothertown-Language",
            github_team="proto-SNEA-admin",
            role="admin"
        )
        # Editor role for the proto-SNEA team
        editor_perm = Permission(
            github_org="Brothertown-Language",
            github_team="proto-SNEA",
            role="editor"
        )
        # Viewer role for the proto-SNEA-viewer team
        viewer_perm = Permission(
            github_org="Brothertown-Language",
            github_team="proto-SNEA-viewer",
            role="viewer"
        )
        session.add_all([admin_perm, editor_perm, viewer_perm])
        session.commit()
        print("SUCCESS: Seeded default permissions for Brothertown-Language.")
    except Exception as e:
        session.rollback()
        print(f"ERROR: Failed to seed permissions: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_permissions()
