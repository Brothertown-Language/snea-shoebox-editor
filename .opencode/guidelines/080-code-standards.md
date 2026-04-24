# Code Standards

## Scope

These standards apply to **ALL code artifacts**: Python modules, Jupyter notebooks, LaTeX/XeLaTeX documents, configuration files, scripts, and any other code written or modified in this repository. No exceptions.

## Typing

- Mandatory explicit type hints (Pydantic/Dataclasses) project-wide. Avoid `Any`; use concrete types wherever possible.
  `Any` is acceptable only when imposed by third-party signatures.
- Use Python 3.12+ built-in types (`list[str]`, `dict[str, Any]`), not `typing.List`/`Dict`.
- **Strict Enum Mapping**: DB-stored enums use plain string values (`NEW_DISCOVERY = "new_discovery"`).
  Emojis/presentation strings handled as properties or mapping functions, never stored in DB.
- **Parsing Logic Changes**: Changes to `src/commons/parsing/` affecting extracted metadata require a full pipeline
  rerun from Step 100 (`0100_ingest_xml.ipynb`) — performed by the user, not the agent. A change **affects extracted
  metadata** if it alters the values, presence, or format of any field written to the database or output files. Agent
  MUST NOT write DB remediation, backfill, or migration code to compensate for parsing changes; the pipeline rerun
  handles data consistency. Flag the rerun requirement to the user after making such changes. Redundant "safety-net"
  updates in downstream notebooks prohibited.

## Design Principles

> **For design principles (KISS, DRY, SRP, SoC, cohesion, YAGNI, Fail Fast, Defensive Programming, and all 20 programming principles), see the `programming-principles` skill.** That skill is the single authoritative source for both enforcement rules and design judgment (apply strongly when / relax when). This guideline retains only project-specific conventions below.

The following project-specific code structure rules are enforced in this repository:

- **Non-Monolithic**: Break large blocks into cohesive, independent components. Notebooks should have focused cells — cells that do "one thing."
- **Single Function Methods**: Every function/method performs exactly ONE task. If a function has multiple responsibilities, split it. Decompose ALL tasks, plans, and algorithms into discrete single-function methods. This applies to:
  - Python functions in `.py` files
  - Notebook cells (each cell should do ONE thing)
  - LaTeX/XeLaTeX environments and macros (one purpose each)
  - Scripts and configuration files
- **No Monoliths**: Long procedural blocks are prohibited. If a function exceeds 40 lines, decompose it. If a notebook cell exceeds 50 lines, split it into multiple cells.
- **No Magic Strings or Numbers**: All literal strings and numbers that carry domain meaning must be extracted to named constants (`UPPER_SNAKE_CASE` at module level, or class-level `ClassVar`) before use. Inline literals are only acceptable for truly universal values (e.g., `0`, `1`, `""`, `True`, `False`, HTTP status `200`).
- **No Re-exports** (ABSOLUTE PROHIBITION):
  - NEVER add `from X import Y` or `__all__` to `__init__.py` files.
  - `__init__.py` must contain ONLY a module docstring describing the package purpose.
  - All imports must reference concrete module paths (e.g., `from commons.mesh.validator import MeshValidator`, NOT `from commons.mesh import MeshValidator`).
  - Rationale: Re-exports break IDE "Find Usages" and "Go to Definition" by creating false source locations.
  - Existing `__all__` entries in legacy files are assumed approved — do not remove them without explicit instruction.
  - When creating a NEW `__init__.py`, it must be docstring-only. When editing an existing `__init__.py`, do not add any imports or `__all__` entries.
- **Top-Level Documentation**: Every Python source file must include a brief top-level comment identifying the package's or class's purpose. Use a module docstring (preferred) or a leading `#` comment. Keep it to one or two concise sentences — enough for `.opencode/tools/py ls` to display alongside the filename.
- **Docstring/Comment Determinism**: Pydoc/docstrings and code comments must use deterministic wording. Avoid ambiguous hedge/alternative phrasing such as `maybe`, `if ... or ...`, `and/or`, or `A + B or C` when describing required behavior, validation paths, or implementation intent.
- **Labels Over Index Numbers**: When editing structured artifacts (notebooks, migration lists, cell arrays, ordered configs), add and use stable labels/names so that inserts, deletes, and moves which change index numbers do not cause edit failures. Reference items by label, not by positional index.

## Modern Python

- **Pathlib**: `pathlib.Path` exclusively for file/dir ops. No `os.path.join`, `os.mkdir`, string concatenation. Use `/`
  operator.
- **f-strings**: For all string interpolation. No `.format()` or `%` unless required by external libs.
- **Metadata Integrity**: Use `shutil.copy2` (not `shutil.copy`). Never discard metadata unless explicitly instructed.

## Libraries & Packages

- Use NLP packages (e.g., NLTK) for NLP tasks — no regex for NLP. NLP tasks include tokenization, stemming,
  lemmatization, part-of-speech tagging, named entity recognition, and sentence segmentation. Simple pattern matching
  or fixed-format extraction does not qualify and may use regex. For tasks requiring complex pattern logic beyond
  simple fixed-format extraction, prefer FSM or LALR-type grammars (e.g., `lark`, `pyparsing`) over regex — regex is
  brittle on live data.
- All DB/system ops use existing project libraries. Direct data file manipulation prohibited unless instructed.
- Use `ConfigurationManager` for all data file paths — never hardcode or assume data file locations.
  `project-config.ini` is located at project root; initialize `ConfigurationManager` with the project root path (
  resolved via root resolution per `210-scripting.md`).

## Print Statements & Output

- **NO narration/signal prints**: Never add print statements that narrate code changes, signal feature updates, or announce implementation details. Print statements are for data output and user-facing information only.
- **NO pedantic notes in code**: Lines like `print("Note: X now uses Y")` or `print("Feature Z implemented")` are prohibited. Code should speak for itself through documentation and version control.
- **Valid print uses**: Progress bars, data summaries, error messages, user-facing status, diagnostic output during development/testing.
- **Invalid print uses**: Announcing "implementation complete", narrating changes, signaling "now using X", helpful hints, tutorial-style output, any form of self-documentation via print.
- **Examples of prohibited prints**:
  - `print("Note: Visualizations now use dark mode")`
  - `print("Feature X enabled")`
  - `print("Using new algorithm for Y")`
  - `print("Implementation complete - phase 1")`
- **If context is needed**: Add a docstring, code comment, or update documentation — never a print statement.

## Linting & Static Analysis

- Run appropriate dev tools (linters, type checkers) listed in AGENTS.md "Build / Lint / Test Commands" on all modified Python files before submitting.

## Tool Selection by File Type

### 🚫 PROHIBITED Misuse

**DO NOT run Python tools on non-Python files:**

| Tool | Python Files | Markdown Files |
| -- | -- | -- |
| `ruff` | ✅ REQUIRED | 🚫 PROHIBITED |
| `pyright` | ✅ REQUIRED | 🚫 PROHIBITED |
| `vulture` | ✅ OPTIONAL | 🚫 PROHIBITED |
| `pymarkdownlnt` | 🚫 PROHIBITED | ✅ REQUIRED |
| `mdformat` | 🚫 PROHIBITED | ✅ REQUIRED |

Running `ruff check` or `ruff format` on `.md` files is a **CRITICAL GUIDELINE VIOLATION**.

### Correct Tool Usage

**Python files (`.py`):**

```bash
uvx ruff check --fix src/ test/   # Lint + auto-fix
uvx ruff format src/ test/        # Format
uvx pyright src/                  # Type check
uvx vulture src/                  # Dead code scan
```

**Markdown files (`.md`):**

```bash
uvx pymarkdownlnt scan -r .opencode/guidelines/ docs/   # Lint
uvx mdformat .opencode/guidelines/ docs/                # Format
```

**Rationale:** Python linters (`ruff`, `pyright`, `vulture`) are designed for Python syntax and will produce incorrect or useless results when run on markdown files. Use markdown-specific tools (`pymarkdownlnt`, `mdformat`) for markdown files.

## Numbering — ENFORCED

All enumeration lists, numbered sections, and step sequences in documentation MUST use **natural counting** (starting at 1).

**Prohibited:**

- Zero-indexed numbered lists (`0. First item`, `1. Second item`)
- Step 0 in procedures (use Step 1 as the first step)
- Phase 0 in specs (use Phase 1 as the first phase)

**Exceptions:**

- Code comments explaining 0-indexed array access
- Technical documentation explicitly explaining zero-based indexing concepts

**Rationale:** Documentation is for humans. Natural counting matches human cognition.

**Grandfather clause:** Existing skill files, guideline files, and documentation that use 0-based counting (Step 0, Phase 0) are exempt from this rule. Only newly created or substantially updated files must comply. When updating an existing file that uses 0-based counting, only new or changed sections need to comply — existing 0-based sections are preserved.

## AI Co-Authored Attribution (MANDATORY)

**AI-generated creative content MUST include co-authored attribution where the content format supports it.**

### What Counts as AI-Generated Content

AI co-authorship applies to **creative, original content authored by AI**:

- Original code written by AI
- Original documentation written by AI
- Original designs/architectures conceived by AI
- New modules, classes, functions created by AI

### What Does NOT Require AI Attribution

**Standard/boilerplate content does NOT require AI attribution:**

- Standard licenses (MIT, Apache, GPL, etc.) - these are established legal templates
- Auto-generated files (lock files, build artifacts, `__pycache__`)
- Framework boilerplate (default configs, standard project structures)
- Minor edits to existing files (typo fixes, formatting)
- Files with no creative content (empty `__init__.py`, pure config)

**Copy-pasted content from ANY external source does NOT get AI attribution:**

- Code copied from Stack Overflow, blogs, tutorials
- Code copied from other projects/repositories
- Documentation copied from official sources
- Configuration copied from templates/examples
- **If it was copy-pasted, it's NOT AI-co-authored** - the original source holds copyright

**Rationale:** AI attribution is about transparency in creative work. Copying a standard MIT license, copying code from Stack Overflow, or copy-pasting documentation from another project requires no AI creativity - those sources hold their own copyrights. Only genuinely original content created by AI deserves AI co-authorship attribution.

### Files Requiring Attribution (In-Repository)

| File Type | Attribution Location | Format |
| -- | -- | -- |
| Python files (`.py`) | Module docstring | `"""Co-authored with AI: <AgentName> (<ModelId>)"""` |
| README files | Footer section | `## Co-Authored With AI` section |
| New repositories | README.md | AI co-authored section (see below) |
| Original docs | Footer | `*Co-authored with AI: <AgentName> (<ModelId>)*` |

### Posted Content Requiring Attribution

| Content Type | Attribution Location | Format |
| -- | -- | -- |
| Issue comments (any repository) | Last line of comment body | `🤖 Co-authored with AI: <AgentName> (<ModelId>)` |
| PR comments (any repository) | Last line of comment body | `🤖 Co-authored with AI: <AgentName> (<ModelId>)` |
| PR bodies (AI-authored) | Last line before horizontal rule or end of body | `🤖 Co-authored with AI: <AgentName> (<ModelId>)` |
| Issue bodies (AI-authored) | Last line of issue body | `🤖 Co-authored with AI: <AgentName> (<ModelId>)` |

External repository posts have HIGHER attribution priority than internal content. External posts represent the project to third parties — attribution is a transparency and ethical requirement, not optional.

### Standalone Byline Correction — FORBIDDEN

**Adding a standalone comment whose sole purpose is to append a byline to a previous comment is ABSOLUTELY FORBIDDEN.**

When a byline is missing from AI-authored posted content:

| Option | When | Action |
| -- | -- | -- |
| **Edit the comment** | Platform supports edit + agent has edit permission | Edit the original comment, append byline as last line |
| **Delete + repost** | Agent has delete permission | Delete original, repost with byline included |
| **Accept the omission** | No edit/delete permission | Leave it. Do NOT add a separate byline comment. |

The byline must be **part of the content body**, never a separate message.

### Files NOT Requiring Attribution

| File Type | Reason |
| -- | -- |
| LICENSE files | Standard legal templates (MIT, Apache, etc.) |
| `pyproject.toml`, `setup.py` | Boilerplate configuration |
| Lock files (`uv.lock`, `package-lock.json`) | Auto-generated |
| Empty `__init__.py` | No content |
| Standard `.gitignore` | Established template |
| Copy-pasted code/docs | Original source holds copyright |

### Attribution Format

```
Co-authored with AI: <AgentName> (<ModelId>)
```

**Example:**

```
Co-authored with AI: <AgentName> (<ModelId>)
```

### Repository Creation

When creating a new repository, the README MUST include:

```markdown
## Co-Authored With AI

This repository was created with assistance from AI:

- **AI Agent**: <AgentName>
- **Model**: <ModelId>
- **Date**: YYYY-MM-DD
```

**Note:** The LICENSE file uses standard MIT license without modification. AI attribution goes in README, not LICENSE.

### Python Files

Every Python file with original AI-authored code MUST include attribution in the module docstring:

```python
"""Module description.

Co-authored with AI: <AgentName> (<ModelId>)
"""
```

### Why This Matters

AI co-authored attribution:

1. Maintains transparency about content origin
2. Follows emerging best practices for AI-assisted work
3. Enables proper credit and traceability
4. Helps identify AI-generated content for review
5. **Respects copyright** - only claims co-authorship on genuinely original AI work

## Enforcement Test Mandate for Guideline and Skill Changes

Guideline files (`.opencode/guidelines/*.md`) and skill files (`.opencode/skills/*/SKILL.md`, `.opencode/skills/*/tasks/*.md`) are enforcement-critical documents that control AI agent behavior. Changes to these files MUST be accompanied by corresponding enforcement test updates.

### Behavioral Enforcement Tests (PRIMARY)

Behavioral enforcement tests verify that the agent actually behaves differently after a rule change. They send a prompt to the agent and verify the response actions (tool calls, decline patterns, explicit questions), not just whether rule text exists in a file.

**Principle:** Behavioral tests answer "Does the agent actually behave differently?" Content-verification tests answer "Does the rule text exist in the file?" Both are needed, but behavioral is the PRIMARY enforcement gate.

**Root case:** Bug #1217 demonstrated that the agent had all the correct guideline text about verification but still answered a general knowledge question with zero tool-call verification. Content-verification alone was insufficient — the agent behavior did not match the rule text.

Every critical violation change MUST have at least one behavioral test that verifies the agent follows the new rule. Behavioral tests use the assertion helpers in `.opencode/tests/behaviors/helpers.sh`:

- `assert_tool_calls_made` — verify the agent made at least N tool calls of a specified type
- `assert_forbidden_pattern_absent` — verify the agent's response does NOT contain a specified pattern (e.g., `(unverified)` tags)
- `assert_required_pattern_present` — verify the agent's response DOES contain a specified pattern (e.g., decline-to-answer language)
- `assert_skill_invoked` — verify a specific skill was invoked
- `assert_no_skill_invoked` — verify a specific skill was NOT invoked when it shouldn't be

### Content-Verification Tests (SECONDARY)

Content-verification tests verify that rule text exists in the correct files. They are a supplementary sanity check — they confirm the rule was written down but do NOT prove the agent follows it.

Content-verification tests are valuable as a fast check that files haven't regressed, but they MUST NOT be the only enforcement gate for a behavioral rule change. A rule change with only a content-verification test is NOT verified — it only proves the text was written, not that the agent follows it (see #1217).

### 🚫 PROHIBITED

- Adding a critical violation section without a BEHAVIORAL enforcement test that verifies the agent's actual response
- Adding a verification step to a skill without a BEHAVIORAL enforcement test that validates the agent follows it
- Creating a new guideline without a BEHAVIORAL enforcement test that sends a prompt and verifies the agent's behavior
- Modifying a guideline or skill without updating the corresponding BEHAVIORAL enforcement test
- Content-verification tests (checking rule text exists) as the ONLY enforcement for a behavioral rule change
- Running `opencode-cli run` directly without the `with-test-home` wrapper

### ✅ REQUIRED

- Every guideline/skill change comes with a BEHAVIORAL enforcement test that verifies agent behavior
- Content-verification tests as a supplementary sanity check, NOT the primary enforcement gate
- Add the BEHAVIORAL test FIRST (RED), then make the change (GREEN) — behavioral TDD for rules
- Run `bash .opencode/tests/behaviors/run-all.sh` for behavioral tests
- Run `bash .opencode/tests/test-enforcement.sh` for content-verification tests
- Use `bash .opencode/tests/with-test-home opencode-cli run '<message>'` for all opencode-cli testing — never run bare `opencode-cli run`
- Clean up test homes after testing: `bash .opencode/tests/with-test-home --clean-all`

### Per-Change TDD Pattern

| TDD Phase | Action |
| -- | -- |
| **RED** | Write a BEHAVIORAL test that sends a prompt and expects the agent to follow the new rule (test fails because agent doesn't follow it yet); optionally add a content-verification test |
| **GREEN** | Make the guideline/skill change that causes the agent to follow the rule |
| **REFACTOR** | Verify content-verification also passes; clean up test scenarios; confirm behavioral test passes reliably |
| **COMMIT** | Both the behavioral test, content-verification test (if any), and the guideline/skill change committed together |

### Why This Matters

Enforcement tests are the verification layer that proves agent guidelines are actually enforceable. A guideline without a behavioral test is a suggestion, not a rule. A skill without a behavioral test is documentation, not enforcement. Bug #1217 proved that content-verification alone is insufficient — the agent had correct rule text but did not follow the rule in practice.

The `with-test-home` wrapper prevents SQLite session conflicts between the desktop app and CLI tests.

**See `090-incremental-build.md` for the incremental implementation discipline that governs HOW these changes are delivered.** **See `.opencode/tests/README.md` for the enforcement test template and usage guide. See `.opencode/tests/behaviors/` for behavioral test infrastructure, helpers, and template.**

### SC-to-Test Traceability (MANDATORY) — Behavioral PRIMARY

Every spec success criterion MUST have at least one corresponding BEHAVIORAL enforcement test assertion that references the SC ID. The assertion must include a comment linking it to the specific SC:

```bash
# SC-2: agent declines to answer without verification
assert_forbidden_pattern_absent "(unverified)" "unverified escape hatch" || OVERALL_RESULT=1
```

The SC ID comment convention is now a REQUIREMENT, not a convention. Every enforcement test that verifies a spec success criterion MUST include a `# SC-N:` comment prefix identifying which SC it covers.

Content-verification tests (checking rule text existence) are SECONDARY — they supplement behavioral tests but MUST NOT be the only enforcement for behavioral rule changes.

### RED-Phase Ordering (BEHAVIORAL PRIMARY) — MANDATORY

The BEHAVIORAL enforcement test for each SC MUST exist and FAIL before implementation of that SC begins. This is the behavioral TDD cycle:

1. **RED**: Write the BEHAVIORAL enforcement test that verifies the SC (send a prompt, assert the agent follows the rule — test fails because the change doesn't exist yet)
2. **GREEN**: Implement the change that makes the agent follow the rule
3. **REFACTOR**: Verify content-verification also passes; clean up test scenarios
4. **COMMIT**: Both the behavioral test and the change committed together

Writing behavioral tests AFTER implementation means the test was never RED — it never caught the gap between the rule and the agent's behavior. The #1217 root cause was exactly this: the agent had correct rule text (passed content-verification) but did not follow the rule in practice (would have failed behavioral verification).

If SC-to-test traceability is missing any behavioral test for any SC, or if behavioral test assertions were written after implementation (GREEN-without-RED), implementation MUST NOT proceed until the behavioral tests are added and shown to fail first.

## Behavioral RED/GREEN as Primary Enforcement Gate

Content-verification tests (grep for text presence) are SECONDARY. Behavioral tests (verify agent behavior changes) are PRIMARY. This hierarchy is enforced at every workflow step where rule changes are made or approved.

### The Behavioral RED/GREEN Gate

The TDD RED/GREEN cycle for rule changes MUST use behavioral enforcement tests, not just content-verification tests:

1. **RED phase**: Write a behavioral enforcement test that sends the agent a prompt and verifies the agent does NOT follow the new rule yet. The test MUST FAIL at this point because the rule change hasn't been made. Use assertion helpers from `.opencode/tests/behaviors/helpers.sh` (`assert_tool_calls_made`, `assert_forbidden_pattern_absent`, `assert_required_pattern_present`, `assert_skill_invoked`).
2. **GREEN phase**: Make the guideline/rule change and re-run the behavioral test. The test MUST PASS because the agent now follows the rule.
3. **No exceptions**: This gate applies to ALL rule changes — guideline files, skill files, task files, critical violation sections, system prompt blocks.

### 🚫 PROHIBITED (for behavioral rule changes)

- Content-verification tests (grep patterns) as the ONLY enforcement for a behavioral rule change
- Marking a rule change as "tested" when only text presence was verified — the agent having correct rule text does NOT prove it follows the rule
- Writing behavioral tests AFTER implementation (GREEN-without-RED) — the test must be RED first, then GREEN
- Bypassing the behavioral gate because a content-verification test already exists for the same rule
- Claiming a rule is "enforced" based solely on content-verification without behavioral evidence

### ✅ REQUIRED (for behavioral rule changes)

- Every critical violation change MUST have at least one behavioral test verifying the agent follows the new rule
- Behavioral tests are PRIMARY — they prove the agent's behavior actually changed
- Content-verification tests are SECONDARY — they confirm rule text exists but do NOT prove agent compliance
- Add the behavioral test FIRST (RED), then make the change (GREEN) — behavioral TDD for rules
- The behavioral RED/GREEN gate is enforced at every workflow step: spec creation, plan creation, plan execution, and approval gate

### Root Case

Bug #1217 demonstrated that the agent had all the correct guideline text about verification but still answered a general knowledge question with zero tool-call verification. Content-verification alone was insufficient — the agent behavior did not match the rule text. This is why behavioral tests are PRIMARY: they verify that the agent actually behaves differently, not just that the rule text exists.

## Cross-Reference Standards

**Cross-references in specs, issues, and documentation MUST use stable anchors, NOT line numbers.**

### Required Format

| Reference Type | Format | Example |
| -- | -- | -- |
| Function | `file.py` `function_name()` | `process_data()` in `pubmed_client.py` |
| Class | `file.py` `ClassName` | `MeshValidator` in `validator.py` |
| Section | `file.md` `"Section Name"` | `"Cross-Reference Standards"` in `080-code-standards.md` |
| Code snippet | Include snippet (\<20 lines) | See examples below |

### Forbidden Format

| Reference Type | Format | Why Forbidden |
| -- | -- | -- |
| Line number | `file.py:42` | Breaks on every edit |
| Line range | `file.py:42-48` | Breaks on every edit |
| Bare number | "line 42" | No context, breaks on edit |

### Why This Matters

Line numbers shift when:

- Lines are added above the reference
- Lines are deleted above the reference
- Any edit changes file length

Stable anchors (function names, class names, section headers) remain valid across edits.

### Examples

**❌ WRONG (Line Numbers):**

```
See `file.py:42` for the function definition.
See `guidelines.md:150` for the rule.
```

**✅ CORRECT (Stable Anchors):**

```
See `process_data()` in `file.py` for the function definition.
See `"Cross-Reference Standards"` section in `guidelines.md` for the rule.
```

## Parameter Naming Convention

Session-init and env-loader are two independent pipelines with separate naming conventions:

| Pipeline | Source | Output Format | Consumer | Example |
| -- | -- | -- | -- | -- |
| LLM context | session-init (Python) | Dotted `scope.param` | Agent system prompt | `github.owner` |
| Bash environment | env-loader.ts (TypeScript) | UPPER_CASE | Shell commands, Python scripts | `GIT_OWNER` |

**Session-init dotted names** (use in skill files, guidelines, dispatch contexts):
`github.owner`, `github.repo`, `github.platform`, `github.html_url`, `gitbucket.owner`, `gitbucket.repo`, `gitbucket.html_url`, `gitbucket.ssh_url`, `gitbucket.has_credentials`, `srclight.project`, `dev.name`, `dev.email`, `branch`, `worktree.path`, `worktree.fatal`

**Env-loader UPPER_CASE names** (use in bash scripts, Python env reads):
`GIT_OWNER`, `GIT_REPO`, `GIT_PLATFORM`, `GITHUB_HTML_URL`, `GITBUCKET_HTML_URL`, `GITBUCKET_SSH_URL`, `GITBUCKET_HAS_CREDENTIALS`, `DEV_NAME`, `DEV_EMAIL`, `BRANCH_NAME`, `WORKTREE_PATH`, `WORKTREE_FATAL`

These pipelines are independent. Changing session-init output names does NOT require changes to env-loader, and vice versa.
