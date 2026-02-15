#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
proto_snea_pipeline.py

End‑to‑end pipeline:
    MDF → parsed records → normalized → sorted → XeLaTeX output

This is the minimal, explicit, reproducible version.
You will extend the field‑mapping logic as your Proto‑SNEA
schema becomes more detailed.
"""

import unicodedata
from pathlib import Path
from typing import List, Dict, Tuple
import re


# ============================================================
# 1. MDF PARSER (full v3.0, any tag order)
# ============================================================

FIELD_RE = re.compile(r"^\\([A-Za-z0-9_]+)\s*(.*)$")

def parse_mdf_lines(lines: List[str]) -> List[Dict]:
    records = []
    current_record = None
    current_marker = None
    current_value_lines = []

    def flush_field():
        nonlocal current_marker, current_value_lines, current_record
        if current_record is None or current_marker is None:
            current_value_lines = []
            return
        value = "\n".join(current_value_lines).rstrip()
        current_record["ordered_fields"].append((current_marker, value))
        current_record["fields"].setdefault(current_marker, []).append(value)
        current_value_lines = []

    def start_record():
        nonlocal current_record, current_marker, current_value_lines
        if current_record is not None:
            flush_field()
            records.append(current_record)
        current_record = {"ordered_fields": [], "fields": {}}
        current_marker = None
        current_value_lines = []

    for raw in lines:
        line = raw.rstrip("\n")

        if not line.strip():
            if current_marker:
                current_value_lines.append("")
            continue

        m = FIELD_RE.match(line)
        if m:
            marker, rest = m.group(1), m.group(2)

            if marker == "lx":
                start_record()
            elif current_record is None:
                start_record()

            flush_field()
            current_marker = marker
            current_value_lines = [rest] if rest else []
        else:
            if current_marker:
                current_value_lines.append(line)

    if current_record:
        flush_field()
        records.append(current_record)

    return records


def parse_mdf_file(path: Path) -> List[Dict]:
    return parse_mdf_lines(path.read_text(encoding="utf-8").splitlines())


# ============================================================
# 2. NORMALIZATION + SORTING
# ============================================================

def nfd_first_letter(s: str) -> str:
    if not s:
        return "#"
    nfd = unicodedata.normalize("NFD", s)
    return nfd[0].upper()


def normalize_and_sort(records: List[Dict]) -> List[Dict]:
    for r in records:
        lx = r["fields"].get("lx", [""])[0]
        r["lexeme"] = lx
        r["_nfd"] = unicodedata.normalize("NFD", lx)
        r["_letter"] = nfd_first_letter(lx)

    return sorted(records, key=lambda r: r["_nfd"])


# ============================================================
# 3. MDF → Proto‑SNEA FIELD MAPPING
# ============================================================

def mdf_to_proto_snea(rec: Dict) -> Dict:
    """
    Convert raw MDF fields into the structured dict expected
    by the XeLaTeX generator.

    You will extend this mapping as needed.
    """

    f = rec["fields"]

    entry = {
        "headword": f.get("lx", [""])[0],
        "reconstruction": f.get("lx", [""])[0],  # override if needed
        "variants": f.get("va", []),
        "pos": f.get("ps", [""])[0] if "ps" in f else "",
        "gloss": f.get("ge", [""])[0] if "ge" in f else "",
        "morphology": f.get("mr", [""])[0] if "mr" in f else "",
        "notes": "\n".join(f.get("nt", [])),
        "etymology": "\n".join(f.get("et", [])),
        "correspondences": "",  # you will fill this from your own data
        "examples": [],
        "subentries": [],
    }

    # Examples: MDF uses xv (vernacular), xe (English), so (source)
    xv = f.get("xv", [])
    xe = f.get("xe", [])
    so = f.get("so", [])

    for i in range(max(len(xv), len(xe), len(so))):
        entry["examples"].append({
            "form": xv[i] if i < len(xv) else "",
            "gloss": xe[i] if i < len(xe) else "",
            "source": so[i] if i < len(so) else "",
        })

    # Subentries: MDF uses \se
    for se_val in f.get("se", []):
        entry["subentries"].append({
            "headword": se_val,
            "pos": "",     # fill from ps if subentry has its own ps
            "gloss": "",   # fill from ge if subentry has its own ge
            "examples": [],
        })

    return entry


# ============================================================
# 4. XELATEX RENDERING
# ============================================================

def render_entry(e: Dict) -> str:
    lines = []
    hw = e["headword"]

    lines.append(f"\\begin{{entry}}{{{hw}}}")
    lines.append(f"  \\headword{{{hw}}}")

    if e["reconstruction"]:
        lines.append(f"  \\reconstruction{{{e['reconstruction']}}}")

    if e["variants"]:
        lines.append(f"  \\variant{{{', '.join(e['variants'])}}}")

    if e["pos"]:
        lines.append(f"  \\pos{{{e['pos']}}}")

    if e["gloss"]:
        lines.append(f"  \\gloss{{{e['gloss']}}}")

    if e["morphology"]:
        lines.append(f"  \\morphology{{{e['morphology']}}}")

    # Examples
    if e["examples"]:
        lines.append("  \\begin{examples}")
        for ex in e["examples"]:
            if ex["form"]:
                lines.append(f"    \\vernacular{{{ex['form']}}}")
            if ex["gloss"]:
                lines.append(f"    \\english{{{ex['gloss']}}}")
            if ex["source"]:
                lines.append(f"    \\exsource{{{ex['source']}}}")
        lines.append("  \\end{examples}")

    # Subentries
    for sub in e["subentries"]:
        lines.append(f"  \\begin{{subentry}}{{{sub['headword']}}}")
        if sub["pos"]:
            lines.append(f"    \\pos{{{sub['pos']}}}")
        if sub["gloss"]:
            lines.append(f"    \\gloss{{{sub['gloss']}}}")
        lines.append("  \\end{subentry}")

    if e["etymology"]:
        lines.append(f"  \\etymology{{{e['etymology']}}}")

    if e["notes"]:
        lines.append(f"  \\notes{{{e['notes']}}}")

    lines.append("\\end{entry}")
    lines.append("")
    return "\n".join(lines)


def generate_latex(records: List[Dict]) -> str:
    out = []
    current_letter = None

    for r in records:
        letter = r["_letter"]
        if letter != current_letter:
            current_letter = letter
            out.append(f"\\lettersection{{{letter}}}\n")

        out.append(render_entry(mdf_to_proto_snea(r)))

    return "\n".join(out)


# ============================================================
# 5. MAIN
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python proto_snea_pipeline.py <input.mdf> <output.tex>")
        sys.exit(1)

    infile = Path(sys.argv[1])
    outfile = Path(sys.argv[2])

    records = parse_mdf_file(infile)
    records = normalize_and_sort(records)

    latex_body = generate_latex(records)
    outfile.write_text(latex_body, encoding="utf-8")

    print(f"Wrote {outfile}")
