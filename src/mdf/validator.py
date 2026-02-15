# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import re
from typing import List, Optional, Dict, Any
from .tag_loader import get_valid_tags

class MDFValidator:
    r"""
    Validates MDF (Multi-Dictionary Form) data.
    Hierarchy: \lx -> \ps -> \ge
    """

    REQUIRED_HIERARCHY = ["lx", "ps", "ge"]
    LEGACY_TAG_MAPPING = {
        "lmm": "lx",
        "ctg": "ps",
        "gls": "ge",
        "src": "rf",
        "etm": "et",
        "rmk": "nt",
        "cmt": "nt",
        "twn": "cf",
        "drv": "dr"
    }

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
        tag_pattern = re.compile(r"^\s*\\([a-z]+)")
        valid_tags = get_valid_tags()

        # 1. First pass: Identify tags and check basic formatting
        for line in lines:
            line_content = line.strip()
            if not line_content:
                diagnostics.append({"status": "ok", "message": ""})
                continue
                
            match = tag_pattern.match(line_content)
            if not match:
                diagnostics.append({
                    "status": "note",
                    "message": "Recommendation: Start this line with a backslash and tag code (e.g., \\lx) to follow standard MDF formatting."
                })
                continue
            
            tag = match.group(1)
            found_req_tags.append(tag)
            
            # Check for legacy tags
            if tag in MDFValidator.LEGACY_TAG_MAPPING:
                modern = MDFValidator.LEGACY_TAG_MAPPING[tag]
                diagnostics.append({
                    "status": "suggestion",
                    "message": f"Legacy tag \\{tag} detected. Consider updating to the modern MDF form \\{modern}.",
                    "tag": tag
                })
            elif tag not in valid_tags:
                diagnostics.append({
                    "status": "note",
                    "message": f"Unrecognized MDF tag \\{tag}. Please verify if this follows the standard MDF specification.",
                    "tag": tag
                })
            else:
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
            # Find first line with a tag to attach the missing tags note
            target_idx = -1
            for i, d in enumerate(diagnostics):
                if "tag" in d:
                    target_idx = i
                    break
            
            if target_idx != -1:
                # If it's already a suggestion/note, we might append or keep it.
                # Here we prepend the missing tags message if it was "ok"
                if diagnostics[target_idx]["status"] == "ok":
                    diagnostics[target_idx]["status"] = "suggestion"
                    missing_str = ", ".join([f"\\{t}" for t in missing])
                    diagnostics[target_idx]["message"] = (
                        f"Note: This record is missing suggested tags ({missing_str}). "
                        f"Including {hierarchy_str} is recommended for standard MDF compatibility."
                    )

        return diagnostics
