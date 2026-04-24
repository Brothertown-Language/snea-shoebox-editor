"""
Pre-submission secret scanning for GitHub API calls.

Scans content destined for GitHub (issue comments, issue bodies, PR descriptions)
for secrets before submission. Blocks submission if secrets are detected.
"""

import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(
        r"(?:TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL|API_KEY|PRIVATE_KEY|ACCESS_TOKEN)"
        r'\s*[=:]\s*["\']?\S+["\']?',
        re.IGNORECASE,
    ),
    re.compile(r"://[^:]+:([^@]+)@"),
    re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"),
    re.compile(r"glpat-[A-Za-z0-9\-]{20,}"),
]

BLOCKLIST_EXTENSIONS = {".pem", ".key"}
BLOCKLIST_FILES = {"secrets.toml", "credentials.json"}


def scan_content(content: str) -> list[dict]:
    """Scan content for secrets. Returns list of findings."""
    findings = []
    for i, line in enumerate(content.split("\n"), 1):
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(
                    {
                        "line": i,
                        "type": "secret_pattern",
                        "match": match.group(),
                        "pattern": pattern.pattern,
                    }
                )
    return findings


def redact_content(content: str) -> str:
    """Redact secrets in content, returning cleaned version."""
    for pattern in SECRET_PATTERNS:
        content = pattern.sub("[REDACTED]", content)
    return content


def check_baseline(baseline_path: Path = Path(".secrets.baseline")) -> bool:
    """Check if detect-secrets baseline exists."""
    return baseline_path.exists()
