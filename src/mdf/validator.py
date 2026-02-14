# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
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
        diagnostics = MDFValidator.diagnose_record(lines)
        errors = [d["message"] for d in diagnostics if d["status"] == "error"]
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def diagnose_record(lines: List[str]) -> List[Dict[str, str]]:
        """
        Diagnoses each line of an MDF record for structural integrity.
        Returns a list of dicts: {"status": "ok"|"error"|"warning", "message": "..."}
        """
        diagnostics = []
        found_req_tags = []
        tag_pattern = re.compile(r"\\([a-z]+)")

        # 1. First pass: Identify tags and check basic formatting
        for line in lines:
            line = line.strip()
            if not line:
                diagnostics.append({"status": "ok", "message": ""})
                continue
                
            match = tag_pattern.match(line)
            if not match:
                diagnostics.append({
                    "status": "error",
                    "message": "Line does not start with a valid MDF tag (e.g., \\lx)."
                })
                continue
            
            tag = match.group(1)
            found_req_tags.append(tag)
            diagnostics.append({"status": "ok", "message": "", "tag": tag})

        # 2. Second pass: Check Hierarchy and Order
        last_req_idx = -1
        for i, diag in enumerate(diagnostics):
            if "tag" not in diag:
                continue
                
            tag = diag["tag"]
            if tag in MDFValidator.REQUIRED_HIERARCHY:
                req_idx = MDFValidator.REQUIRED_HIERARCHY.index(tag)
                if req_idx < last_req_idx:
                    diag["status"] = "error"
                    diag["message"] = f"Tag \\{tag} is out of order (must follow previous required tags)."
                last_req_idx = req_idx

        # 3. Global Check: Missing Tags (attach to first line for visibility)
        missing = [t for t in MDFValidator.REQUIRED_HIERARCHY if t not in found_req_tags]
        if missing and diagnostics:
            if diagnostics[0]["status"] == "ok":
                diagnostics[0]["status"] = "warning"
                diagnostics[0]["message"] = f"Missing required tags: {', '.join(['\\'+t for t in missing])}"

        return diagnostics
