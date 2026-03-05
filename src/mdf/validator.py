# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import re
from typing import List, Optional, Dict, Any
from .tag_loader import get_valid_tags

class MDFValidator:
    r"""
    Validates MDF (Multi-Dictionary Form) data.
    Hierarchy follows the official MDF recommended field order:
      \lx -> \ps -> \sn -> \ge -> ... -> \nt -> \so -> \dt
    See: docs/mdf/original/MDFields19a_UTF8.txt (Order_of_Fields)
    """

    REQUIRED_HIERARCHY = [
        "lx",   # lexical entry — always first
        "hm",   # homonym number
        "lc",   # lexical citation
        "ph",   # phonetic form
        "se",   # subentry (section boundary)
        "ps",   # part of speech (section boundary)
        "pn",   # part of speech-national
        "sn",   # sense number (section boundary)
        "ge",   # gloss-English
        "de",   # definition-English
        "rf",   # reference
        "xv",   # example-vernacular
        "xe",   # example-English
        "cf",   # cross-reference
        "sy",   # synonyms
        "an",   # antonyms
        "et",   # etymology
        "nt",   # notes
        "so",   # source of data (near end)
        "st",   # status
        "dt",   # datestamp
    ]
    BASIC_TAGS = ["lx", "ps", "ge"]  # Minimum meaningful entry per MDF Basic set
    LEGACY_TAG_MAPPING = {
        "lmm": "lx",
        "ctg": "ps",
        "gls": "ge",
        "src": "rf",
        "etm": "et",
        "rmk": "nt",
        "cmt": "nt",
        "twn": "cf",
        "drv": "dr",
        # Paradigm legacy tags
        "1s": "pdv", "2s": "pdv", "3s": "pdv", "4s": "pdv",
        "1d": "pdv", "2d": "pdv", "3d": "pdv", "4d": "pdv",
        "1p": "pdv", "1i": "pdv", "1e": "pdv", "2p": "pdv", "3p": "pdv", "4p": "pdv",
        # Other discontinued tags
        "xg": None,  # Discontinued field
        "na": "ee"   # Anthropology -> Ethnology
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
        tag_pattern = re.compile(r"^\s*\\([a-z0-9]+)")
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
                if modern:
                    diagnostics.append({
                        "status": "suggestion",
                        "message": f"Legacy tag \\{tag} detected. Consider updating to the modern MDF form \\{modern}.",
                        "tag": tag
                    })
                else:
                    diagnostics.append({
                        "status": "suggestion",
                        "message": f"Discontinued MDF tag \\{tag} detected. This field is no longer recognized in standard MDF.",
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

        # 2. Global Check: Missing Tags (attach to first line for visibility)
        missing = [t for t in MDFValidator.BASIC_TAGS if t not in found_req_tags]
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
                        "Including \\lx, \\ps, and \\ge is recommended for standard MDF compatibility."
                    )

        return diagnostics
