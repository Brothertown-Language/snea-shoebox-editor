"""Preflight verification of a deploy target secrets store against the
required-secrets manifest (issue #1397, SC-2).

Compares a store mapping (nested dict, e.g. a parsed secrets structure)
against the manifest's dotted key paths and returns a structured report
naming missing key PATHS only. Values are never read, returned, or logged —
the comparison is key-presence only (SC-5 value-safety).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MANIFEST_PATH = Path(".streamlit") / "required_secrets.yaml"


def load_required_secret_paths() -> list[str]:
    """Load the required dotted key paths from the required-secrets manifest.

    The manifest is the single source of truth for required ``st.secrets``
    key paths (SC-1); both the preflight check (SC-2) and the startup guard
    (SC-3) consume this loader so they cannot silently diverge.

    Returns:
        List of dotted key paths, in manifest order.
    """
    import yaml

    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return list(data["required_secrets"])


def _lookup(store: Mapping[str, Any], segments: Sequence[str]) -> bool:
    """Return True when the dotted path exists in the nested store mapping."""
    node: Any = store
    for seg in segments:
        if not isinstance(node, Mapping) or seg not in node:
            return False
        node = node[seg]
    return True


def check_required_secrets(
    store: Mapping[str, Any],
    manifest_paths: Sequence[str],
) -> dict[str, list[str]]:
    """Compare a secrets store mapping against the manifest's required paths.

    Args:
        store: Nested mapping representing the parsed secrets store.
        manifest_paths: Required dotted key paths from the manifest.

    Returns:
        Structured report ``{"missing": [<dotted paths>]}`` naming missing
        key PATHS only. Never contains or logs secret values.
    """
    missing = [path for path in manifest_paths if not _lookup(store, path.split("."))]
    if missing:
        logger.info("missing required secrets: %s", ", ".join(missing))
    else:
        logger.info("required secrets preflight passed: all %d keys present", len(manifest_paths))
    return {"missing": missing}
