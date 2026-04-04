#!/usr/bin/env python3
"""
Anchor reference verification script.

Detects fragile reference patterns in guideline and skill files:
- Section numbers: §123, §123.45
- Step numbers: Step 5
- Gate numbers: Gate 2
- Phase numbers: Phase 3
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # .opencode/skills/approval-gate -> project root


@dataclass
class FragileRef:
    """A fragile reference found in a file."""

    file: Path
    line_num: int
    ref_type: str
    ref_value: str
    line_content: str


def find_section_refs(content: str) -> List[tuple]:
    """Find §number references."""
    # Pattern: §123 or §123.45
    pattern = r"§(\d+(?:\.\d+)?)"
    return [(m.start(), m.group()) for m in re.finditer(pattern, content)]


def find_step_refs(content: str) -> List[tuple]:
    """Find Step X references."""
    # Pattern: Step 5 (case insensitive, word boundary)
    pattern = r"\b(Step\s+\d+)\b"
    return [(m.start(), m.group()) for m in re.finditer(pattern, content, re.IGNORECASE)]


def find_gate_refs(content: str) -> List[tuple]:
    """Find Gate X references."""
    # Pattern: Gate 2 (case insensitive, word boundary)
    pattern = r"\b(Gate\s+\d+)\b"
    return [(m.start(), m.group()) for m in re.finditer(pattern, content, re.IGNORECASE)]


def find_phase_refs(content: str) -> List[tuple]:
    """Find Phase X references."""
    # Pattern: Phase 3 (case insensitive, word boundary)
    # Exclude "Phase N" where N is a description like "Phase 1: Infrastructure"
    pattern = r"\b(Phase\s+\d+)\b(?!\s*:)"
    results = []
    for m in re.finditer(pattern, content, re.IGNORECASE):
        # Check if it's followed by colon (skip those as they're section headers)
        start = m.start()
        if start + len(m.group()) < len(content):
            next_char = content[start + len(m.group())]
            if next_char not in ":":
                results.append((start, m.group()))
        else:
            results.append((start, m.group()))
    return results


def scan_file(filepath: Path) -> List[FragileRef]:
    """Scan a file for fragile references."""
    try:
        content = filepath.read_text()
    except Exception as e:
        print(f"error: {filepath}: {e}", file=sys.stderr)
        return []

    refs = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip code blocks and inline code
        if "`" in line:
            # Skip content in backticks
            continue

        # Find references in this line
        for pos, ref in find_section_refs(line):
            refs.append(FragileRef(filepath, line_num, "section", ref, line.strip()))

        for pos, ref in find_step_refs(line):
            refs.append(FragileRef(filepath, line_num, "step", ref, line.strip()))

        for pos, ref in find_gate_refs(line):
            refs.append(FragileRef(filepath, line_num, "gate", ref, line.strip()))

        for pos, ref in find_phase_refs(line):
            refs.append(FragileRef(filepath, line_num, "phase", ref, line.strip()))

    return refs


def main():
    """Scan all guideline and skill files for fragile references."""
    guidelines_dir = PROJECT_ROOT / ".opencode" / "guidelines"
    skills_dir = PROJECT_ROOT / ".opencode" / "skills"

    all_refs = []

    # Scan guideline files
    for md_file in sorted(guidelines_dir.glob("*.md")):
        refs = scan_file(md_file)
        all_refs.extend(refs)

    # Scan skill files
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir():
            for md_file in sorted(skill_dir.glob("*.md")):
                refs = scan_file(md_file)
                all_refs.extend(refs)

    # Also scan AGENTS.md
    agents_file = PROJECT_ROOT / "AGENTS.md"
    if agents_file.exists():
        refs = scan_file(agents_file)
        all_refs.extend(refs)

    # Report results
    if not all_refs:
        print("✅ No fragile references found")
        return 0

    # Group by file
    by_file = {}
    for ref in all_refs:
        key = str(ref.file.relative_to(PROJECT_ROOT))
        if key not in by_file:
            by_file[key] = []
        by_file[key].append(ref)

    print(f"❌ Found {len(all_refs)} fragile references in {len(by_file)} files:\n")

    for filepath in sorted(by_file.keys()):
        refs = by_file[filepath]
        print(f"\n{filepath}:")
        for ref in refs:
            print(f"  Line {ref.line_num:4d}: {ref.ref_type:8s} {ref.ref_value}")
            print(f"            {ref.line_content[:70]}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
