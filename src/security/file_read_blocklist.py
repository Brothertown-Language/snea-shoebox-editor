"""
File read blocklist with value redaction.

When the agent's read tool accesses a blocklisted file, this module provides
redaction functionality that preserves key names while replacing secret values
with [REDACTED:TYPE] markers.
"""

import re
from fnmatch import fnmatch
from pathlib import Path

BLOCKLIST_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "secrets.toml",
    "credentials.json",
]

SECRET_KEY_WORDS = ("TOKEN", "KEY", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "PRIVATE_KEY", "ACCESS_TOKEN")

SECRETS_REDACTED_HEADER = (
    "⚠️ SECRETS REDACTED — this file contains sensitive values that have been replaced with [REDACTED:TYPE] markers\n\n"
)


def _type_label_for_key(key_name: str) -> str:
    """Determine the TYPE label for a secret key."""
    upper = key_name.upper().rstrip("=: ")
    if upper.endswith("PASSWORD") or upper == "PASSWORD":
        return "PASSWORD"
    if upper.endswith("CREDENTIAL") or upper == "CREDENTIAL":
        return "CREDENTIAL"
    return "TOKEN"


def is_blocklisted(file_path: str) -> bool:
    """Check if a file path matches any blocklist pattern."""
    name = Path(file_path).name
    for pattern in BLOCKLIST_PATTERNS:
        if fnmatch(name, pattern):
            return True
    return False


def redact_file_content(content: str, file_path: str = "") -> str:
    """Redact secret values in file content.

    Preserves key names and structure, replaces values with [REDACTED:TYPE].
    Adds a header warning.
    """
    redacted = content

    # URL-embedded passwords: protocol://user:password@host → protocol://user:[REDACTED:PASSWORD]@host
    redacted = re.sub(
        r"://([^:]+):([^@]+)@",
        lambda m: f"://{m.group(1)}:[REDACTED:PASSWORD]@",
        redacted,
    )

    # Standalone GitHub/GitLab tokens
    redacted = re.sub(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}", "[REDACTED:TOKEN]", redacted)
    redacted = re.sub(r"\bglpat-[A-Za-z0-9\-]{20,}", "[REDACTED:TOKEN]", redacted)

    # Assignment patterns: KEYNAME=value, KEYNAME="value", KEYNAME='value'
    # Matches key names that end with or are exactly one of the secret keywords
    key_pattern = "|".join(SECRET_KEY_WORDS)

    def _replace_assignment(m: re.Match) -> str:
        prefix = m.group(1)  # "KEYNAME=" or "KEYNAME: " etc.
        quote = m.group(2)  # opening quote or empty
        _value = m.group(3)  # the secret value
        # Extract key name from prefix
        key_match = re.match(r"(\w+)\s*[=:]", prefix)
        key_name = key_match.group(1) if key_match else ""
        type_label = _type_label_for_key(key_name)
        closing = quote  # closing quote matches opening
        return f"{prefix}{quote}[REDACTED:{type_label}]{closing}"

    redacted = re.sub(
        rf'((?:\w*(?:{key_pattern}))\s*[=:]\s*)(["\']?)([^\s"\'#]+?)\2',
        _replace_assignment,
        redacted,
        flags=re.IGNORECASE,
    )

    return SECRETS_REDACTED_HEADER + redacted
