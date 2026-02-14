# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import re
from typing import List, Optional, Dict, Any

class MDFValidator:
    r"""
    Validates MDF (Multi-Dictionary Form) data.
    Hierarchy: \lx -> \ps -> \ge
    """

    REQUIRED_HIERARCHY = ["lx", "ps", "ge"]

    @staticmethod
    def validate_record(lines: List[str]) -> Dict[str, Any]:
        """
        Validates a single MDF record.
        Always returns valid: True for linguistic records as they are
        always valid for export/editing.
        """
        return {
            "valid": True,
            "errors": []
        }

    @staticmethod
    def diagnose_record(lines: List[str]) -> List[Dict[str, str]]:
        """
        Diagnoses each line of an MDF record for structural integrity.
        Returns a list of dicts: {"status": "ok"|"suggestion"|"note", "message": "..."}
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
                    "status": "note",
                    "message": "Recommendation: Start this line with a backslash and tag code (e.g., \\lx) to follow standard MDF formatting."
                })
                continue
            
            tag = match.group(1)
            found_req_tags.append(tag)
            diagnostics.append({"status": "ok", "message": "", "tag": tag})

        # 2. Second pass: Check Hierarchy and Order
        last_req_idx = -1
        hierarchy_str = " -> ".join([f"\\{t}" for t in MDFValidator.REQUIRED_HIERARCHY])
        
        for i, diag in enumerate(diagnostics):
            if "tag" not in diag:
                continue
                
            tag = diag["tag"]
            
            # \se and \sn start new nested entries or senses, resetting hierarchy
            if tag in ["se", "sn"]:
                last_req_idx = -1
                diag["status"] = "ok"
                diag["message"] = ""
                continue

            if tag in MDFValidator.REQUIRED_HIERARCHY:
                req_idx = MDFValidator.REQUIRED_HIERARCHY.index(tag)
                if req_idx < last_req_idx:
                    diag["status"] = "suggestion"
                    diag["message"] = (
                        f"Tag \\{tag} is out of order. While not required, MDF records usually follow "
                        f"this hierarchy: {hierarchy_str}. You may reorder tags to match this "
                        "suggested sequence."
                    )
                last_req_idx = req_idx

        # 3. Global Check: Missing Tags (attach to first line for visibility)
        missing = [t for t in MDFValidator.REQUIRED_HIERARCHY if t not in found_req_tags]
        if missing and diagnostics:
            if diagnostics[0]["status"] == "ok":
                diagnostics[0]["status"] = "suggestion"
                missing_str = ", ".join([f"\\{t}" for t in missing])
                diagnostics[0]["message"] = (
                    f"Note: This record is missing suggested tags ({missing_str}). "
                    f"Including {hierarchy_str} is recommended for standard MDF compatibility."
                )

        return diagnostics
