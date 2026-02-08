# Copyright (c) 2026 Brothertown Language
"""
Script to verify the ISO 639-3 table is loaded and report stats.
Usage: uv run python scripts/verify_iso639.py
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

from src.database.connection import get_session
from src.database.models.iso639 import ISO639_3
from sqlalchemy import func

def verify_iso639():
    """Verify ISO 639-3 table and report statistics."""
    session = get_session()
    try:
        total_count = session.query(ISO639_3).count()
        
        print("\n" + "="*80)
        print("ISO 639-3 TABLE VERIFICATION")
        print("="*80)
        print(f"Total records found: {total_count}")
        
        if total_count == 0:
            print("\nWARNING: The ISO 639-3 table is EMPTY.")
            print("The data is automatically seeded when the application starts or via init_db().")
        else:
            # Breakdown by Scope
            print("\nBreakdown by Scope:")
            print("-" * 30)
            scope_stats = session.query(ISO639_3.scope, func.count(ISO639_3.id)).group_by(ISO639_3.scope).all()
            for scope, count in scope_stats:
                scope_desc = {
                    'I': 'Individual',
                    'M': 'Macrolanguage',
                    'S': 'Special'
                }.get(scope, scope)
                print(f"{scope_desc:<20}: {count}")

            # Breakdown by Language Type
            print("\nBreakdown by Language Type:")
            print("-" * 30)
            type_stats = session.query(ISO639_3.language_type, func.count(ISO639_3.id)).group_by(ISO639_3.language_type).all()
            for l_type, count in type_stats:
                type_desc = {
                    'L': 'Living',
                    'E': 'Extinct',
                    'A': 'Ancient',
                    'H': 'Historic',
                    'C': 'Constructed',
                    'S': 'Special'
                }.get(l_type, l_type)
                print(f"{type_desc:<20}: {count}")

            # Sample SNEA-relevant languages if they exist
            print("\nSample Relevant Languages:")
            print("-" * 30)
            relevant_codes = ['alg', 'wam', 'mof', 'skw', 'nrp'] # Algonquian, Massachusett, Mohegan-Pequot, Skepi Creole, Narragansett (nrp is often used or similar)
            # Actually let's just search for some names
            samples = session.query(ISO639_3).filter(ISO639_3.id.in_(relevant_codes)).all()
            for s in samples:
                print(f"[{s.id}] {s.ref_name} ({s.scope}/{s.language_type})")

        print("="*80 + "\n")

    except Exception as e:
        print(f"Error verifying ISO 639-3 data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_iso639()
