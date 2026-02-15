#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
mdf_to_html.py

Standalone MDF → HTML dictionary generator.
- Parses full MDF v3.0 (any tag order)
- Normalizes headwords to NFD
- Sorts alphabetically by first NFD codepoint
- Maps MDF → Proto‑SNEA dictionary fields
- Emits a complete HTML document (no external dependencies)

This is the HTML twin of your XeLaTeX generator.
"""

import unicodedata
from pathlib import Path
from typing import List, Dict
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
    f = rec["fields"]

    entry = {
        "headword": f.get("lx", [""])[0],
        "reconstruction": f.get("lx", [""])[0],
        "variants": f.get("va", []),
        "pos": f.get("ps", [""])[0] if "ps" in f else "",
        "gloss": f.get("ge", [""])[0] if "ge" in f else "",
        "morphology": f.get("mr", [""])[0] if "mr" in f else "",
        "notes": "\n".join(f.get("nt", [])),
        "etymology": "\n".join(f.get("et", [])),
        "examples": [],
        "subentries": [],
    }

    xv = f.get("xv", [])
    xe = f.get("xe", [])
    so = f.get("so", [])

    for i in range(max(len(xv), len(xe), len(so))):
        entry["examples"].append({
            "form": xv[i] if i < len(xv) else "",
            "gloss": xe[i] if i < len(xe) else "",
            "source": so[i] if i < len(so) else "",
        })

    for se_val in f.get("se", []):
        entry["subentries"].append({
            "headword": se_val,
            "pos": "",
            "gloss": "",
            "examples": [],
        })

    return entry


# ============================================================
# 4. HTML RENDERING
# ============================================================

def render_entry_html(e: dict) -> str:
    hw = e.get("headword", "")
    html = []

    html.append(f'<div class="entry" id="{hw}">')
    html.append(f'  <h2 class="headword">{hw}</h2>')

    if e.get("reconstruction"):
        html.append(f'  <div class="reconstruction"><strong>Reconstruction:</strong> {e["reconstruction"]}</div>')

    if e.get("variants"):
        html.append(f'  <div class="variants"><strong>Variants:</strong> {", ".join(e["variants"])}</div>')

    if e.get("pos"):
        html.append(f'  <div class="pos"><strong>Category:</strong> {e["pos"]}</div>')

    if e.get("gloss"):
        html.append(f'  <div class="gloss"><strong>Gloss:</strong> {e["gloss"]}</div>')

    if e.get("morphology"):
        html.append(f'  <div class="morphology"><strong>Morphology:</strong> {e["morphology"]}</div>')

    if e.get("examples"):
        html.append('  <div class="examples"><strong>Examples:</strong><ul>')
        for ex in e["examples"]:
            html.append('    <li>')
            if ex["form"]:
                html.append(f'      <span class="example-form">{ex["form"]}</span>')
            if ex["gloss"]:
                html.append(f'      <span class="example-gloss"> — {ex["gloss"]}</span>')
            if ex["source"]:
                html.append(f'      <span class="example-source"> ({ex["source"]})</span>')
            html.append('    </li>')
        html.append('  </ul></div>')

    if e.get("subentries"):
        html.append('  <div class="subentries">')
        for sub in e["subentries"]:
            html.append(f'    <div class="subentry" id="{hw}-{sub["headword"]}">')
            html.append(f'      <h3 class="subentry-headword">{sub["headword"]}</h3>')
            if sub.get("pos"):
                html.append(f'      <div class="pos"><strong>Category:</strong> {sub["pos"]}</div>')
            if sub.get("gloss"):
                html.append(f'      <div class="gloss"><strong>Gloss:</strong> {sub["gloss"]}</div>')
            html.append('    </div>')
        html.append('  </div>')

    if e.get("etymology"):
        html.append(f'  <div class="etymology"><strong>Etymology:</strong> {e["etymology"]}</div>')

    if e.get("notes"):
        html.append(f'  <div class="notes"><strong>Notes:</strong> {e["notes"]}</div>')

    html.append('</div>')
    html.append('')
    return "\n".join(html)


def render_letter_section_html(letter: str) -> str:
    return f'<h1 class="letter-section">{letter}</h1>'


def generate_html(records: List[Dict]) -> str:
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('  <meta charset="UTF-8">')
    html.append('  <title>Proto‑SNEA Dictionary</title>')
    html.append('  <style>')
    html.append('    body { font-family: serif; max-width: 800px; margin: auto; padding: 2em; }')
    html.append('    .entry { margin-bottom: 2em; }')
    html.append('    .letter-section { margin-top: 2em; border-bottom: 1px solid #aaa; }')
    html.append('  </style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<div id="dictionary">')

    current_letter = None

    for rec in records:
        letter = rec["_letter"]
        if letter != current_letter:
            current_letter = letter
            html.append(render_letter_section_html(letter))

        entry = mdf_to_proto_snea(rec)
        html.append(render_entry_html(entry))

    html.append('</div>')
    html.append('</body>')
    html.append('</html>')

    return "\n".join(html)


# ============================================================
# 5. MAIN
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python mdf_to_html.py <input.mdf> <output.html>")
        sys.exit(1)

    infile = Path(sys.argv[1])
    outfile = Path(sys.argv[2])

    records = parse_mdf_file(infile)
    records = normalize_and_sort(records)

    html = generate_html(records)
    outfile.write_text(html, encoding="utf-8")

    print(f"Wrote {outfile}")
