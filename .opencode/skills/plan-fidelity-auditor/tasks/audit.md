# Task: audit

## Purpose

Full audit workflow: extract problem statement, generate clean-room plan, invoke compare task, invoke report task, post findings.

## Procedure

1. **Read the spec issue** via GitHub MCP
2. **Extract problem statement** (Objective, Problem Statement, Context, Constraints, Success Criteria)
3. **Write to clean-room input** at `./tmp/clean-room-input-N.md`
4. **Assess problem statement clarity** — if vague, recommend brainstorming
5. **Generate clean-room plan** by invoking `writing-plans --task clean-room`
6. **Invoke compare task** to compare clean-room against existing plan
7. **Invoke report task** to report all findings
8. **Post findings** to GitHub Issue as comment
9. **Clean up** delete `./tmp/clean-room-input-N.md`

## Vague Problem Statement Handling

If the problem statement extracted from the spec is vague:
- **Report VAGUE_PROBLEM finding** with severity HIGH
- **Recommend brainstorming** rather than proceeding with comparison
- Do NOT attempt to generate a clean-room plan from a vague problem statement

## Failure Recovery

If the writing-plans subtask fails:
1. Log the failure in the audit comment
2. Post a warning that plan fidelity could not be verified
3. Continue with remaining subtasks (if called within orchestrator)
4. Do NOT block the audit on clean-room generation failure

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs
- No auto-updates to the issue
- Clean-room plan is a comparison artifact only
- Must use GitHub MCP tools for all issue operations

Co-authored with AI: <AI-Name> (<model-id>)