#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""
Skill card validation only (sensor mode). Corrections are agent-driven.

Validates SKILL.md files per spec #1124:
  REQ-1: Frontmatter validation (name, description, type, license, compatibility)
  REQ-2: Placeholder enforcement (no hardcoded identity values)
  REQ-3: Worktree Mode section requirement for skills with bash/git/file ops

Usage:
    uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py           # validate
    uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py --json   # JSON output

Exit codes: 0 = all pass, 1 = any fail
"""

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

VALID_TYPES = {"discipline-enforcing", "technique", "pattern", "reference", "orchestrator"}
HARDCODED_AGENT_NAMES = re.compile(r"\bOpenCode\b|\bClaude\b|\bCopilot\b|\bGemini\b|\bGPT-4\b")
HARDCODED_MODEL_IDS = re.compile(
    r"\bollama-cloud/[a-z0-9._-]+\b"
    r"|claude-3[-_]5[-_]sonnet"
    r"|claude-3-opus"
    r"|claude-3-sonnet"
    r"|gpt-4[a-z0-9-]*"
    r"|glm-[0-9.]+"
)
HARDCODED_DEV_NAMES = re.compile(r"\bexample-developer\b|\bexample-dev-alias\b")
HARDCODED_ORG_REPO = re.compile(r"\bexample-org\b|\bexample-repo\b")
ATTRIBUTION_EXEMPT = re.compile(r"Co-authored with AI:.*<AgentName>.*<ModelId>")
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
WORKTREE_MODE_HEADING_RE = re.compile(r"^##\s+Worktree\s+Mode", re.MULTILINE | re.IGNORECASE)
FILE_OPS_PATTERN = re.compile(
    r"`?read`?|`?write`?|`?edit`?|`?glob`?|`?grep`?"
    r"|\bbash\b.*tool\b|\bgit\s+\w"
    r"|worktree\.path",
    re.IGNORECASE,
)


class Violation(NamedTuple):
    violation_type: str
    skill_name: str
    rule_id: str
    message: str
    detail: str = ""
    file_path: str = ""
    line_approx: int | None = None


def discover_skill_cards(root: Path) -> list[Path]:
    cards = sorted(root.glob(".opencode/skills/*/SKILL.md"))
    cards.extend(sorted(root.glob(".opencode/skills/*/platforms/*/SKILL.md")))
    return cards


def parse_frontmatter(content: str) -> tuple[dict[str, str], str, str]:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}, "", content
    fm_text = match.group(1)
    body = content[match.end() :]
    fields: dict[str, str] = {}
    for line in fm_text.split("\n"):
        colon = line.find(":")
        if colon > 0:
            key = line[:colon].strip()
            val = line[colon + 1 :].strip()
            fields[key] = val
    return fields, fm_text, body


def skill_name_from_path(p: Path) -> str:
    parts = p.parts
    idx = parts.index("skills")
    return "/".join(parts[idx + 1 : -1])


def validate_req1(name: str, fields: dict[str, str], fm_text: str, file_path: str) -> list[Violation]:
    violations: list[Violation] = []
    if "name" not in fields:
        violations.append(Violation("REQ-1", name, "name", "Missing 'name' field", file_path=file_path))
    else:
        val = fields["name"]
        if not re.match(r"^[a-z0-9-]+$", val):
            violations.append(
                Violation("REQ-1", name, "name", f"Name '{val}' not hyphen-case", val, file_path=file_path)
            )
        elif val.startswith("-") or val.endswith("-") or "--" in val:
            violations.append(
                Violation("REQ-1", name, "name", f"Name '{val}' has bad hyphens", val, file_path=file_path)
            )
    if "description" not in fields:
        violations.append(Violation("REQ-1", name, "description", "Missing 'description' field", file_path=file_path))
    else:
        desc = fields["description"]
        if not desc.startswith("Use when"):
            violations.append(
                Violation(
                    "REQ-1",
                    name,
                    "description",
                    "Description doesn't start with 'Use when'",
                    desc[:60],
                    file_path=file_path,
                )
            )
        if "<" in desc or ">" in desc:
            violations.append(
                Violation(
                    "REQ-1", name, "description", "Description contains angle brackets", desc[:60], file_path=file_path
                )
            )
    if "type" not in fields:
        violations.append(Violation("REQ-1", name, "type", "Missing 'type' field", file_path=file_path))
    elif fields["type"] not in VALID_TYPES:
        violations.append(
            Violation("REQ-1", name, "type", f"Invalid type '{fields['type']}'", fields["type"], file_path=file_path)
        )
    if "license" not in fields:
        violations.append(Violation("REQ-1", name, "license", "Missing 'license' field", file_path=file_path))
    if "compatibility" not in fields:
        violations.append(
            Violation("REQ-1", name, "compatibility", "Missing 'compatibility' field", file_path=file_path)
        )
    return violations


def validate_req2(name: str, content: str, file_path: str) -> list[Violation]:
    violations: list[Violation] = []
    content_no_code = CODE_BLOCK_RE.sub("", content)
    lines_no_code = content_no_code.split("\n")
    for i, line in enumerate(lines_no_code):
        if ATTRIBUTION_EXEMPT.search(line):
            continue
        for pattern, label, placeholder in [
            (HARDCODED_AGENT_NAMES, "agent name", "<AgentName>"),
            (HARDCODED_MODEL_IDS, "model ID", "<ModelId>"),
            (HARDCODED_DEV_NAMES, "developer name", "<dev.name>/<dev.email>"),
            (HARDCODED_ORG_REPO, "org/repo name", "<github.owner>/<github.repo>"),
        ]:
            for m in pattern.finditer(line):
                violations.append(
                    Violation(
                        "REQ-2",
                        name,
                        "placeholder",
                        f"Hardcoded {label}: '{m.group()}' — use {placeholder}",
                        f"line~{i + 1}",
                        file_path,
                        i + 1,
                    )
                )
    return violations


def validate_req3(name: str, body: str, file_path: str) -> list[Violation]:
    violations: list[Violation] = []
    if WORKTREE_MODE_HEADING_RE.search(body):
        return violations
    if FILE_OPS_PATTERN.search(body):
        violations.append(
            Violation(
                "REQ-3",
                name,
                "worktree-mode",
                "Missing 'Worktree Mode' section (skill contains bash/git/file operations)",
                file_path=file_path,
            )
        )
    return violations


def validate_card(card_path: Path, root: Path) -> list[Violation]:
    name = skill_name_from_path(card_path.relative_to(root))
    rel_path = str(card_path.relative_to(root))
    content = card_path.read_text(encoding="utf-8")
    fields, fm_text, body = parse_frontmatter(content)
    violations: list[Violation] = []
    if not content.startswith("---"):
        violations.append(Violation("REQ-1", name, "frontmatter", "No YAML frontmatter found", file_path=rel_path))
        return violations
    if not fields:
        violations.append(Violation("REQ-1", name, "frontmatter", "Invalid frontmatter format", file_path=rel_path))
        return violations
    violations.extend(validate_req1(name, fields, fm_text, rel_path))
    violations.extend(validate_req2(name, content, rel_path))
    violations.extend(validate_req3(name, body, rel_path))
    return violations


def violation_to_dict(v: Violation) -> dict:
    return {
        "skill_name": v.skill_name,
        "file_path": v.file_path,
        "violation_type": v.violation_type,
        "rule_id": v.rule_id,
        "message": v.message,
        "detail": v.detail,
        "line_approx": v.line_approx,
    }


def main() -> int:
    if "--fix" in sys.argv:
        print(
            "ERROR: --fix mode has been removed. Autocorrection is now agent-driven.\n"
            "Use the skill-creator validate task for semantic review and correction.\n"
            "Invoke: /skill skill-creator --task validate"
        )
        return 2
    json_mode = "--json" in sys.argv
    root = Path.cwd()
    cards = discover_skill_cards(root)
    if not cards:
        if json_mode:
            print(json.dumps([]))
        else:
            print("No SKILL.md files found.")
        return 1
    all_violations: list[Violation] = []
    for card_path in cards:
        all_violations.extend(validate_card(card_path, root))
    if json_mode:
        print(json.dumps([violation_to_dict(v) for v in all_violations], indent=2))
        return 0 if not all_violations else 1
    print("=== Skill Card Validation ===")
    print(f"Discovered {len(cards)} skill cards\n")
    by_skill: dict[str, list[Violation]] = {}
    for v in all_violations:
        by_skill.setdefault(v.skill_name, []).append(v)
    for card_path in cards:
        name = skill_name_from_path(card_path.relative_to(root))
        violations = by_skill.get(name, [])
        if violations:
            print(f"FAIL  {name}")
            for v in violations:
                print(f"  [{v.violation_type}] {v.rule_id}: {v.message}")
                if v.detail:
                    print(f"         detail: {v.detail}")
        else:
            print(f"PASS  {name}")
    print("\n--- Summary ---")
    print(f"Cards: {len(cards)}, Violations: {len(all_violations)}")
    if all_violations:
        violating_skills = sorted({v.skill_name for v in all_violations})
        print(f"Failing skills: {', '.join(violating_skills)}")
    return 0 if not all_violations else 1


if __name__ == "__main__":
    sys.exit(main())
