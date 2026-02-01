# Copyright (c) 2026 Brothertown Language

import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Iterable
import importlib

# Optional tqdm: use if available, otherwise fall back to plain logging
try:  # pragma: no cover - optional dependency
    _tqdm = importlib.import_module("tqdm").tqdm  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    _tqdm = None  # type: ignore


OWNER = "Brothertown-Language"
REPO = "snea-shoebox-editor"
BRANCH = "main"
WORKFLOW_NAME = "Deploy to Cloudflare"


def read_env_token() -> str:
    # Prefer explicit env vars
    for key in ("GH_TOKEN", "PROD_GH_TOKEN"):
        token = os.environ.get(key)
        if token and token.strip():
            return token.strip()
    # Fallback: read from .env
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for key in ("GH_TOKEN", "PROD_GH_TOKEN"):
                m = re.match(rf"{key}\s*=\s*(.*)\s*", line)
                if m:
                    val = m.group(1).strip().strip('"').strip("'")
                    if val:
                        return val
    raise RuntimeError("GH_TOKEN / PROD_GH_TOKEN not found in environment or .env")


def _log(msg: str) -> None:
    print(f"[download-ci-logs] {msg}")


def gh_get(url: str, token: str) -> bytes:
    _log(f"GET {url}")
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urllib.request.urlopen(req) as resp:
        content_length = int(resp.headers.get("Content-Length", "0") or 0)
        if _tqdm and content_length > 0:
            chunks: list[bytes] = []
            remaining = content_length
            with _tqdm(total=content_length, unit="B", unit_scale=True, desc="download") as bar:
                while remaining > 0:
                    chunk = resp.read(min(65536, remaining))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
                    bar.update(len(chunk))
            return b"".join(chunks)
        else:
            return resp.read()


def gh_download(url: str, token: str, dest: Path) -> None:
    _log(f"DOWNLOAD {url} -> {dest}")
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urllib.request.urlopen(req) as resp:
        content_length = int(resp.headers.get("Content-Length", "0") or 0)
        if _tqdm and content_length > 0:
            with _tqdm(total=content_length, unit="B", unit_scale=True, desc=f"save {dest.name}") as bar:
                with open(dest, "wb") as f:
                    remaining = content_length
                    while remaining > 0:
                        chunk = resp.read(min(65536, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                        bar.update(len(chunk))
        else:
            dest.write_bytes(resp.read())


def main() -> int:
    _log("Starting CI logs download")
    out_dir = Path("tmp/ci-logs")
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        _log("Reading token from env/.env (GH_TOKEN/PROD_GH_TOKEN)")
        token = read_env_token()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    _log("Fetching latest workflow runs")
    runs_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?branch={BRANCH}&per_page=25"
    )
    data = gh_get(runs_url, token)
    payload = json.loads(data.decode("utf-8"))
    runs = payload.get("workflow_runs", [])

    # Pick the latest run whose workflow name matches
    _log(f"Selecting target run for workflow name '{WORKFLOW_NAME}'")
    target = None
    for r in runs:
        if r.get("name") == WORKFLOW_NAME:
            target = r
            break
    if not target and runs:
        # fallback: first run on branch
        target = runs[0]

    if not target:
        _log("No workflow runs found to download.")
        return 0

    run_id = target["id"]
    run_number = target.get("run_number")
    status = target.get("status")
    conclusion = target.get("conclusion")
    html_url = target.get("html_url")

    # Save a brief summary JSON
    summary_path = out_dir / f"run-{run_id}-summary.json"
    summary = {
        "id": run_id,
        "run_number": run_number,
        "status": status,
        "conclusion": conclusion,
        "html_url": html_url,
        "name": target.get("name"),
        "head_branch": target.get("head_branch"),
        "event": target.get("event"),
        "created_at": target.get("created_at"),
        "updated_at": target.get("updated_at"),
    }
    _log(f"Writing summary JSON -> {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2))

    # Download run logs zip
    logs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/logs"
    zip_path = out_dir / f"run-{run_id}-logs.zip"
    _log("Downloading run logs (zip)")
    gh_download(logs_url, token, zip_path)

    # Also fetch per-job logs (text) for quick viewing
    jobs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/jobs?per_page=100"
    _log("Fetching job list for run")
    jobs_payload = json.loads(gh_get(jobs_url, token).decode("utf-8"))
    jobs = jobs_payload.get("jobs", [])
    _log(f"Found {len(jobs)} jobs; downloading individual job logs")
    iterator: Iterable = jobs
    if _tqdm:
        iterator = _tqdm(jobs, desc="jobs", unit="job")
    for job in iterator:
        job_id = job["id"]
        job_name = job.get("name", f"job-{job_id}")
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_name)
        log_txt = out_dir / f"run-{run_id}-{safe_name}.log"
        job_log_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/jobs/{job_id}/logs"
        try:
            gh_download(job_log_url, token, log_txt)
        except Exception as e:
            # Some jobs may not have accessible logs
            log_txt.write_text(f"Failed to download job logs: {e}\n")

    # Produce a quick summary text file
    summary_txt = out_dir / f"run-{run_id}-summary.txt"
    lines = [
        f"Workflow: {summary['name']}",
        f"Run: #{summary['run_number']} (id {summary['id']})",
        f"Branch: {summary['head_branch']}  Event: {summary['event']}",
        f"Status: {summary['status']}  Conclusion: {summary['conclusion']}",
        f"URL: {summary['html_url']}",
        "",
        f"Saved logs: {zip_path}",
    ]
    # Add job names and attempts
    if jobs:
        lines.append("Jobs:")
        for job in jobs:
            lines.append(
                f"- {job.get('name')} (status={job.get('status')}, conclusion={job.get('conclusion')})"
            )
    _log(f"Writing summary text -> {summary_txt}")
    summary_txt.write_text("\n".join(lines) + "\n")

    _log("Done. Saved artifacts:")
    print(f"- {summary_path}")
    print(f"- {zip_path}")
    for job in jobs:
        job_name = job.get("name", f"job-{job['id']}")
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_name)
        print(f"- {out_dir / f'run-{run_id}-{safe_name}.log'}")
    print(f"- {summary_txt}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
