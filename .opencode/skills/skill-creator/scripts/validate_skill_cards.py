#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""
Comprehensive skill card validation and autocorrection system.

Validates SKILL.md files per spec #1124:
  REQ-1: Frontmatter validation (name, description, type, license, compatibility)
  REQ-2: Placeholder enforcement (no hardcoded identity values)
  REQ-3: Worktree Mode section requirement for skills with bash/git/file ops

Usage:
    uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py           # validate only
    uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py --fix     # autocorrect

Exit codes: 0 = all pass, 1 = any fail
"""

import re
import subprocess
import sys
import time
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

WORKTREE_MODE_TEMPLATE = """
## Worktree Mode

When operating in a git worktree (`worktree.path` is set), all file operations
MUST prefix paths with `worktree.path`:

- `read(filePath=f"{worktree.path}/src/main.py")` — not `read(filePath="src/main.py")`
- `edit(filePath=f"{worktree.path}/src/main.py", ...)` — not `edit(filePath="src/main.py", ...)`
- Bash commands: use `workdir=worktree.path` parameter
- `glob(pattern="src/**/*.py", path=worktree.path)` — not `glob(pattern="src/**/*.py")`
- `grep(pattern="TODO", path=f"{worktree.path}/src/")` — not `grep(pattern="TODO", path="src/")`

**When `worktree.path` is NOT set** (main repo): relative paths function as expected.
"""


class Violation(NamedTuple):
    req: str
    skill_name: str
    field: str
    message: str
    detail: str = ""


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


def validate_req1(name: str, fields: dict[str, str], fm_text: str) -> list[Violation]:
    violations: list[Violation] = []
    if "name" not in fields:
        violations.append(Violation("REQ-1", name, "name", "Missing 'name' field"))
    else:
        val = fields["name"]
        if not re.match(r"^[a-z0-9-]+$", val):
            violations.append(Violation("REQ-1", name, "name", f"Name '{val}' not hyphen-case", val))
        elif val.startswith("-") or val.endswith("-") or "--" in val:
            violations.append(Violation("REQ-1", name, "name", f"Name '{val}' has bad hyphens", val))

    if "description" not in fields:
        violations.append(Violation("REQ-1", name, "description", "Missing 'description' field"))
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
                )
            )
        if "<" in desc or ">" in desc:
            violations.append(
                Violation(
                    "REQ-1",
                    name,
                    "description",
                    "Description contains angle brackets",
                    desc[:60],
                )
            )

    if "type" not in fields:
        violations.append(Violation("REQ-1", name, "type", "Missing 'type' field"))
    elif fields["type"] not in VALID_TYPES:
        violations.append(Violation("REQ-1", name, "type", f"Invalid type '{fields['type']}'", fields["type"]))

    if "license" not in fields:
        violations.append(Violation("REQ-1", name, "license", "Missing 'license' field"))

    if "compatibility" not in fields:
        violations.append(Violation("REQ-1", name, "compatibility", "Missing 'compatibility' field"))

    return violations


def validate_req2(name: str, content: str) -> list[Violation]:
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
                    )
                )
    return violations


def validate_req3(name: str, body: str) -> list[Violation]:
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
            )
        )
    return violations


def validate_card(card_path: Path, root: Path) -> list[Violation]:
    name = skill_name_from_path(card_path.relative_to(root))
    content = card_path.read_text(encoding="utf-8")
    fields, fm_text, body = parse_frontmatter(content)
    violations: list[Violation] = []
    if not content.startswith("---"):
        violations.append(Violation("REQ-1", name, "frontmatter", "No YAML frontmatter found"))
        return violations
    if not fields:
        violations.append(Violation("REQ-1", name, "frontmatter", "Invalid frontmatter format"))
        return violations
    violations.extend(validate_req1(name, fields, fm_text))
    violations.extend(validate_req2(name, content))
    violations.extend(validate_req3(name, body))
    return violations


def apply_fixes(card_path: Path, root: Path, violations: list[Violation]) -> bool:
    content = card_path.read_text(encoding="utf-8")
    fields, fm_text, body = parse_frontmatter(content)
    changed = False

    for v in violations:
        if v.field == "type" and v.message.startswith("Missing"):
            fm_text += "\ntype: technique"
            changed = True
        elif v.field == "license" and v.message.startswith("Missing"):
            fm_text += "\nlicense: MIT"
            changed = True
        elif v.field == "compatibility" and v.message.startswith("Missing"):
            fm_text += "\ncompatibility: opencode"
            changed = True
        elif v.field == "description" and "doesn't start with 'Use when'" in v.message:
            if "description" in fields:
                old_desc = fields["description"]
                new_desc = "Use when " + old_desc[0].lower() + old_desc[1:]
                fm_text = fm_text.replace(old_desc, new_desc, 1)
                changed = True
        elif v.field == "description" and "angle brackets" in v.message:
            if "description" in fields:
                old_desc = fields["description"]
                new_desc = old_desc.replace("<", "").replace(">", "")
                fm_text = fm_text.replace(old_desc, new_desc, 1)
                changed = True
        elif v.field == "placeholder" and v.message.startswith("Hardcoded agent name"):
            for agent in ["OpenCode", "Claude", "Copilot", "Gemini", "GPT-4"]:
                content = content.replace(agent, "<AgentName>")
            changed = True
        elif v.field == "placeholder" and v.message.startswith("Hardcoded model ID"):
            content = re.sub(r"\bollama-cloud/[a-z0-9._-]+\b", "<ModelId>", content)
            content = re.sub(r"claude-3[-_]5[-_]sonnet", "<ModelId>", content)
            content = re.sub(r"claude-3-opus", "<ModelId>", content)
            content = re.sub(r"claude-3-sonnet", "<ModelId>", content)
            content = re.sub(r"gpt-4[a-z0-9-]*", "<ModelId>", content)
            content = re.sub(r"\bglm-[0-9.]+\b", "<ModelId>", content)
            changed = True
        elif v.field == "placeholder" and v.message.startswith("Hardcoded developer name"):
            content = content.replace("example-developer", "<dev.name>")
            content = content.replace("example-dev-alias", "<dev.email>")
            changed = True
        elif v.field == "placeholder" and v.message.startswith("Hardcoded org/repo"):
            content = content.replace("example-org", "<github.owner>")
            content = content.replace("example-repo", "<github.repo>")
            changed = True
        elif v.field == "worktree-mode":
            body += WORKTREE_MODE_TEMPLATE
            changed = True

    if changed:
        new_content = f"---\n{fm_text}\n---{body}"
        card_path.write_text(new_content, encoding="utf-8")
    return changed


def run_fix_mode(root: Path, all_violations: dict[str, list[Violation]]) -> None:
    timestamp = int(time.time())
    branch_name = f"fix/skill-card-validation-{timestamp}"
    print("\n=== Autocorrect Mode ===")
    print(f"Creating fix branch: {branch_name}")

    try:
        subprocess.run(["git", "worktree", "list"], capture_output=True, text=True, check=True)
    except Exception:
        current_wt = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        ).stdout.strip()
        if current_wt != str(root):
            print("Already in a worktree — creating branch here instead of new worktree.")
            subprocess.run(["git", "checkout", "-b", branch_name], check=True, cwd=str(root))
        else:
            wt_path = root.parent / f".worktrees/fix-skill-card-validation-{timestamp}"
            subprocess.run(
                ["git", "worktree", "add", str(wt_path), "-b", branch_name],
                check=True,
                cwd=str(root),
            )
            fix_root = wt_path
            cards = discover_skill_cards(fix_root)
            for card_path in cards:
                name = skill_name_from_path(card_path.relative_to(fix_root))
                if name in all_violations and all_violations[name]:
                    applied = apply_fixes(card_path, fix_root, all_violations[name])
                    if applied:
                        print(f"  Fixed: {name}")
            subprocess.run(["git", "add", ".opencode/skills/"], check=True, cwd=str(wt_path))
            subprocess.run(
                ["git", "commit", "-m", "fix(skill-cards): correct validation violations"],
                check=True,
                cwd=str(wt_path),
            )
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, cwd=str(wt_path))
            re_violations = []
            for card_path in cards:
                re_violations.extend(validate_card(card_path, fix_root))
            if re_violations:
                print(f"\nWARNING: {len(re_violations)} violations remain after fix:")
                for v in re_violations:
                    print(f"  [{v.req}] {v.skill_name}: {v.message}")
            else:
                print("All violations resolved after fix.")
            return

    cards = discover_skill_cards(root)
    for card_path in cards:
        name = skill_name_from_path(card_path.relative_to(root))
        if name in all_violations and all_violations[name]:
            applied = apply_fixes(card_path, root, all_violations[name])
            if applied:
                print(f"  Fixed: {name}")

    subprocess.run(["git", "add", ".opencode/skills/"], check=True, cwd=str(root))
    subprocess.run(
        ["git", "commit", "-m", "fix(skill-cards): correct validation violations"],
        check=True,
        cwd=str(root),
    )
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, cwd=str(root))

    re_violations = []
    for card_path in cards:
        re_violations.extend(validate_card(card_path, root))
    if re_violations:
        print(f"\nWARNING: {len(re_violations)} violations remain after fix:")
        for v in re_violations:
            print(f"  [{v.req}] {v.skill_name}: {v.message}")
    else:
        print("All violations resolved after fix.")


def main() -> int:
    fix_mode = "--fix" in sys.argv
    root = Path.cwd()
    cards = discover_skill_cards(root)

    if not cards:
        print("No SKILL.md files found.")
        return 1

    print("=== Skill Card Validation ===")
    print(f"Discovered {len(cards)} skill cards\n")

    all_violations: dict[str, list[Violation]] = {}
    total_violations = 0
    all_pass = True

    for card_path in cards:
        name = skill_name_from_path(card_path.relative_to(root))
        violations = validate_card(card_path, root)
        all_violations[name] = violations
        total_violations += len(violations)
        if violations:
            all_pass = False
            print(f"FAIL  {name}")
            for v in violations:
                print(f"  [{v.req}] {v.field}: {v.message}")
                if v.detail:
                    print(f"         detail: {v.detail}")
        else:
            print(f"PASS  {name}")

    print("\n--- Summary ---")
    print(f"Cards: {len(cards)}, Violations: {total_violations}")

    if not all_pass:
        violating_skills = sorted({v.skill_name for vl in all_violations.values() for v in vl if v})
        print(f"Failing skills: {', '.join(violating_skills)}")

    if fix_mode and not all_pass:
        run_fix_mode(root, all_violations)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
