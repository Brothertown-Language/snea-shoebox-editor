---
name: ui-design
description: Use when designing UI wireframes, mockups, interaction specs, or visual artifacts. Triggers on: ui design, wireframe, mockup, interaction spec, visual layout, UI mock, screenshot capture, sidebar navigation, page layout.
type: technique
license: MIT
compatibility: opencode
---

# UI Design Skill

## Overview

The `ui-design` skill produces toolkit-agnostic design artifacts (wireframes, mockups, interaction specs) that can be consumed by any implementation skill or sub-agent. It operates as a sub-agent dispatched by `divide-and-conquer` or invoked directly via `/skill ui-design`.

**Model assignment:** `kimi-k2.6:cloud`

All design output is framework-neutral. The skill does NOT embed Streamlit, web, Android, Godot, Flutter, or any other framework-specific concepts into its artifacts. Framework binding is the responsibility of `ui-engineer`, not `ui-design`.

## Persona

**UI Design Specialist** — produces clear, implementable design artifacts that separate visual structure from framework implementation. Focuses on information architecture, component relationships, navigation flow, and accessibility requirements.

## Sub-Agent Tasks

| Task | Word Count | Description |
|------|-----------|-------------|
| `design` | ≈800 | Full UI design pass: layout, components, navigation, accessibility |
| `wireframe` | ≈400 | Low-fidelity wireframe from template |
| `mockup` | ≈400 | High-fidelity mockup from template |
| `interaction-spec` | ≈500 | YAML interaction specification from schema |
| `screenshot` | ≈300 | Capture screenshot of rendered artifact |
| `review` | ≈400 | Review design artifact against spec requirements |
| `completion` | ≈200 | Idempotent cleanup and final summary |

Result contracts (returned by each sub-agent):

```yaml
design:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  artifacts: [list of file paths relative to worktree]
  summary: string
  concerns: string (empty if none)

wireframe:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  artifact_path: string (relative to worktree)
  summary: string
  concerns: string (empty if none)

mockup:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  artifact_path: string (relative to worktree)
  summary: string
  concerns: string (empty if none)

interaction-spec:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  artifact_path: string (relative to worktree)
  summary: string
  concerns: string (empty if none)

screenshot:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  artifact_path: string (relative to worktree)
  summary: string
  concerns: string (empty if none)

review:
  status: PASS | CONCERNS | FAIL
  findings: [list of {severity, description, recommendation}]
  summary: string

completion:
  status: DONE
  cleaned_up: [list of temp resources cleaned]
  summary: string
```

## Invocation

```
/skill ui-design --task design
/skill ui-design --task wireframe
/skill ui-design --task mockup
/skill ui-design --task interaction-spec
/skill ui-design --task screenshot
/skill ui-design --task review
/skill ui-design --task completion
```

Dispatch context for sub-agents MUST include: `worktree.path`, `github.owner`, `github.repo`, `dev.name`, `dev.email`, plus any spec or context parameters relevant to the task.

## Operating Protocol

1. **Load spec/context before designing.** Read the relevant spec issue, plan, and any referenced context files before producing any design artifact.
2. **Produce toolkit-agnostic artifacts only.** Wireframes use SVG, mockups use HTML+CSS, interaction specs use YAML per `interaction_spec_schema.yaml`. No framework-specific markup, classes, or patterns.
3. **Never reference specific UI frameworks in design artifacts.** Artifacts must not contain Streamlit, React, Vue, Godot, Flutter, Android, or any other framework-specific terminology. Framework binding is `ui-engineer`'s responsibility.
4. **Use PEP 723 scripts from `scripts/` for rendering and validation.** Call `render_svg_to_png.py`, `render_html_screenshot.py`, `validate_svg.py`, `validate_interaction_spec.py`, etc. via `uv run --script` — never install dependencies globally.
5. **Completion guarantee.** Every task invocation MUST end with the `completion` subtask to clean up temporary resources and produce a final summary. The `completion` task is idempotent and safe to invoke multiple times.

## Trigger Self-Identification (Three Tiers)

### Tier 1: Intelligence (Context Inference)

When the context involves designing screens, layouts, navigation structures, component relationships, or visual hierarchies, and no other skill is more specific, `ui-design` should activate.

### Tier 2: Keyword-Enhanced

- Issue body contains `[UI]` label or `requires-ui: true` field
- Plan phase mentions "wireframe", "mockup", "interaction spec", "visual layout"
- Spec includes UI-related success criteria

### Tier 3: Direct

- `/skill ui-design` explicit invocation
- `--task <task-name>` explicit task selection

## Model Assignment

| Task | Model | Rationale |
|------|-------|-----------|
| All tasks | `kimi-k2.6:cloud` | Strong visual design reasoning, good at structured output |

## Cross-References

- **`ui-engineer`**: Consumes `ui-design` artifacts and binds them to a specific UI framework. The handoff point is the interaction spec and wireframe/mockup files.
- **`divide-and-conquer`**: Dispatches `ui-design` as a sub-agent via `assemble-work` when the plan includes UI design phases.
- **`issue-operations`**: Used for posting progress comments and linking design artifacts to issues.
- **`verification-before-completion`**: Validates design artifacts against spec success criteria before marking the phase complete.