# Copyright (c) 2026 Brothertown Language
"""
Script to dump the local user accounts list and the local user activity list to CSV files.
Usage: uv run python scripts/dump_users.py
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
from src.database.connection import get_session
from src.database.models.identity import User, UserActivityLog

def dump_users(session, output_path):
    """Dump all users to a CSV file and print to console."""
    users = session.query(User).all()
    
    fieldnames = [
        'id', 'email', 'username', 'github_id', 'full_name', 
        'is_active', 'last_login', 'created_at'
    ]
    
    # Print to console for human review
    print("\n" + "="*80)
    print(f"{'ID':<4} | {'Username':<15} | {'Email':<25} | {'Last Login':<20}")
    print("-" * 80)
    for user in users:
        last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
        print(f"{user.id:<4} | {user.username:<15} | {user.email:<25} | {last_login:<20}")
    print("="*80 + "\n")

    # Keep CSV dump for record keeping
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames + ['extra_metadata'])
        writer.writeheader()
        for user in users:
            writer.writerow({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'github_id': user.github_id,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else '',
                'created_at': user.created_at.isoformat() if user.created_at else '',
                'extra_metadata': user.extra_metadata
            })
    print(f"Successfully dumped {len(users)} users to {output_path}")

def dump_activity_logs(session, output_path):
    """Dump all user activity logs to a CSV file."""
    logs = session.query(UserActivityLog).all()
    
    fieldnames = [
        'id', 'user_email', 'session_id', 'action', 'details', 'ip_address', 'timestamp'
    ]
    
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            writer.writerow({
                'id': log.id,
                'user_email': log.user_email,
                'session_id': log.session_id,
                'action': log.action,
                'details': log.details,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat() if log.timestamp else ''
            })
    print(f"Successfully dumped {len(logs)} activity logs to {output_path}")

def main():
    # Ensure tmp directory exists
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    users_csv = tmp_dir / "users_dump.csv"
    activity_csv = tmp_dir / "user_activity_log.csv"
    
    try:
        session = get_session()
        dump_users(session, users_csv)
        dump_activity_logs(session, activity_csv)
    except Exception as e:
        print(f"Error dumping data: {e}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
