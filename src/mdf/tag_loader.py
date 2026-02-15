# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->

import json
import os
from functools import lru_cache
from typing import Set

@lru_cache(maxsize=1)
def get_valid_tags() -> Set[str]:
    """
    Loads the list of valid MDF tags from src/mdf/tags.json.
    Returns a set of strings (tags without the backslash).
    """
    # Relative to this file
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, 'tags.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            tags = json.load(f)
            return set(tags)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to a minimal set if file is missing/broken
        return {"lx", "hm", "ps", "ge", "se", "sn", "xv", "xe", "cf", "va", "ve", "de", "nt"}
