# Copyright (c) 2026 Brothertown Language
"""
Script to dump the AUTH/PERMS table (permissions) for human review.
Usage: uv run python scripts/dump_permissions.py
"""
import sys
import os
from pathlib import Path

# Ensure we are in the project root by navigating relative to this script
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent
os.chdir(project_root)

# Add project root to sys.path to allow importing from src
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

import csv
from sqlalchemy import text
from src.database.connection import get_session
from src.database.models.identity import Permission

def dump_permissions(session, output_path):
    """Dump all permissions to a CSV file and print to console for human review."""
    # Check if table exists first
    try:
        session.execute(text("SELECT 1 FROM permissions LIMIT 1"))
    except Exception:
        print("ERROR: 'permissions' table does not exist or database is not initialized.")
        return

    permissions = session.query(Permission).all()
    
    # Print to console for human review
    print("\n" + "="*95)
    print(f"{'ID':<4} | {'Source':<6} | {'Organization':<25} | {'Team':<25} | {'Role':<10}")
    print("-" * 95)
    
    if not permissions:
        print(" " * 35 + "NO PERMISSIONS FOUND")
    else:
        for p in permissions:
            source = str(p.source_id) if p.source_id is not None else "ALL"
            team = p.github_team if p.github_team else "ALL"
            org = p.github_org if p.github_org else "N/A"
            print(f"{p.id:<4} | {source:<6} | {org:<25} | {team:<25} | {p.role:<10}")
    
    print("="*95 + "\n")

    # Save to CSV in tmp directory
    fieldnames = ['id', 'source_id', 'github_org', 'github_team', 'role', 'created_at']
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in permissions:
            writer.writerow({
                'id': p.id,
                'source_id': p.source_id,
                'github_org': p.github_org,
                'github_team': p.github_team,
                'role': p.role,
                'created_at': p.created_at.isoformat() if p.created_at else ''
            })
    
    if permissions:
        print(f"Successfully dumped {len(permissions)} permissions to {output_path}")

def main():
    # Ensure tmp directory exists
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    permissions_csv = tmp_dir / "permissions_dump.csv"
    
    session = None
    try:
        session = get_session()
        dump_permissions(session, permissions_csv)
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    main()
