# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import sys
import time
import requests
import zipfile
import io

def download_latest_logs(repo="Brothertown-Language/snea-shoebox-editor", workflow_name="Test Suite", branch="main"):
    token = os.getenv("PROD_GH_TOKEN")
    if not token:
        print("ERROR: PROD_GH_TOKEN not set.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    print(f"Polling for latest run of '{workflow_name}' on branch '{branch}'...")
    
    run_id = None
    while True:
        url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=10"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"ERROR: Failed to fetch runs: {response.status_code} {response.text}")
            sys.exit(1)
        
        runs = response.json().get("workflow_runs", [])
        target_run = next((r for r in runs if r["name"] == workflow_name), None)
        
        if not target_run:
            print("No matching run found yet. Retrying in 10s...")
            time.sleep(10)
            continue
            
        run_id = target_run["id"]
        status = target_run["status"]
        conclusion = target_run["conclusion"]
        
        print(f"Current Run ID: {run_id}, Status: {status}, Conclusion: {conclusion}")
        
        if status == "completed":
            break
        
        print("Waiting for run to complete. Polling in 30s...")
        time.sleep(30)

    print(f"Downloading logs for run {run_id}...")
    logs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    log_response = requests.get(logs_url, headers=headers, timeout=10)
    
    if log_response.status_code != 200:
        print(f"ERROR: Failed to download logs: {log_response.status_code}")
        sys.exit(1)
        
    z = zipfile.ZipFile(io.BytesIO(log_response.content))
    output_dir = f"tmp/ci-logs/run-{run_id}"
    os.makedirs(output_dir, exist_ok=True)
    z.extractall(output_dir)
    print(f"Logs extracted to {output_dir}")
    return output_dir

if __name__ == "__main__":
    download_latest_logs()
