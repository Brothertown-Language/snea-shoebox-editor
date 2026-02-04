# Copyright (c) 2026 Brothertown Language
import re
from typing import List, Optional, Dict

class MDFValidator:
    r"""
    Validates MDF (Multi-Dictionary Form) data.
    Hierarchy: \lx -> \ps -> \ge
    """

    REQUIRED_HIERARCHY = ["lx", "ps", "ge"]

    @staticmethod
    def validate_record(lines: List[str]) -> Dict[str, any]:
        """
        Validates a single MDF record.
        Returns a dictionary with 'valid' (bool) and 'errors' (list of str).
        """
        errors = []
        found_tags = []
        
        tag_pattern = re.compile(r"\\([a-z]+)")

        for line in lines:
            match = tag_pattern.match(line)
            if match:
                found_tags.append(match.group(1))

        # Check hierarchy
        # All required tags must exist and be in order relative to each other
        found_req_tags = [tag for tag in found_tags if tag in MDFValidator.REQUIRED_HIERARCHY]
        
        # Check for missing tags
        for req_tag in MDFValidator.REQUIRED_HIERARCHY:
            if req_tag not in found_req_tags:
                errors.append(f"Missing required tag: \\{req_tag}")

        # Check for order
        last_req_idx = -1
        for tag in found_req_tags:
            req_idx = MDFValidator.REQUIRED_HIERARCHY.index(tag)
            if req_idx < last_req_idx:
                errors.append(f"Tag \\{tag} found out of order.")
            last_req_idx = req_idx

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
