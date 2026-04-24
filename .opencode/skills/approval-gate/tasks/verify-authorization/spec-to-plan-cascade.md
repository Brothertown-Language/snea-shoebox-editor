# Task: verify-authorization — Step 5b: Spec-to-Plan Approval Cascade

## Purpose

When a spec is approved and a plan already exists for that spec, the plan inherits the spec's approval status. This eliminates the redundant second approval step when a plan faithfully implements an already-approved spec.

## Conditions

The two-gate model STILL applies when no plan exists at the time of spec approval: spec approval → plan creation → plan approval → implementation. The cascade ONLY activates when a plan already exists.

## 5b.1 Detect Approval Cascade Conditions

This step runs ONLY when the approved issue is a spec (detected in Step 5 Auto-Dispatch context differentiation).

```python
# Determine if this is a spec approval
is_spec = "spec" in [l["name"] for l in issue["labels"]] or issue["title"].startswith("[SPEC")

if not is_spec:
    # Skip cascade — only applies to spec approvals
    proceed to Step 6

# Search for plans referencing this spec
spec_number = issue["number"]
plan_issues = github_search_issues(
    query=f"open label:plan Spec: #{spec_number} repo:{<github.owner>}/{<github.repo>}"
)
```

## 5b.2 Process Cascade Approval

If one or more plans reference the approved spec:

```python
if plan_issues:
    # Multiple plans: approve the most recent, supersede the rest
    if len(plan_issues) > 1:
        # Sort by creation date, most recent first
        plan_issues.sort(key=lambda p: p["created_at"], reverse=True)
        most_recent = plan_issues[0]
        older_plans = plan_issues[1:]

        # Cascade-approve the most recent plan
        github_issue_write(
            method="update",
            issue_number=most_recent["number"],
            labels=[l for l in most_recent["labels"] if l != "needs-approval"],
        )
        github_add_issue_comment(
            issue_number=most_recent["number"],
            body="Approval cascaded from spec #{spec_number}. Plan approved automatically because spec is already approved and this is the most recent plan referencing it.",
        )

        # Supersede older plans
        for old_plan in older_plans:
            github_add_issue_comment(
                issue_number=old_plan["number"],
                body="Superseded by #{most_recent_number} — cascade approval applies to the most recent plan only.",
            )

    else:
        # Single plan: cascade-approve it
        plan_issue = plan_issues[0]
        github_issue_write(
            method="update",
            issue_number=plan_issue["number"],
            labels=[l for l in plan_issue["labels"] if l != "needs-approval"],
        )
        github_add_issue_comment(
            issue_number=plan_issue["number"],
            body="Approval cascaded from spec #{spec_number}. Plan approved automatically because spec is already approved.",
        )

elif not plan_issues:
    # No plan exists — cascade does NOT apply
    # Current flow is correct: spec approval → writing-plans create → plan needs approval
    proceed to Step 6 (auto-dispatch to writing-plans)
```

## 5b.3 Cascade Does NOT Apply When

- The approved issue is a plan (not a spec) — cascade is spec-to-plan only
- No plan exists for the spec — current flow is correct, writing-plans will create a new plan
- The spec has been revised — existing revocation rules apply; cascade approval is revoked per Step 6 "Spec Revision Revocation Detection"
- The plan does not faithfully implement the spec — `plan-fidelity-auditor` catches this during implementation review

**⚠️ Body-Preservation Safeguard:** This task only updates labels (no `body=` parameter in `github_issue_write` calls). Status updates use `github_add_issue_comment`. If any future modification were to use `github_issue_write(method=update, body=...)`, it MUST verify that the new body preserves all original content (len(new_body) >= 0.8 * len(original_body)). See `000-critical-rules.md` → "Critical Violation: Issue Body Erasure" for the project-wide rule.

## 5b.4 Edge Cases

| Edge Case | Handling |
| -- | -- |
| Multiple plans for same spec | Cascade approves the most recent plan by creation date; older plans are superseded |
| Plan created after spec approval | Handled by `writing-plans --task create` post-creation step |
| Spec revised after cascade | Existing revocation rules apply — see Step 6 "Spec Revision Revocation Detection" |
| No plan exists | Cascade does NOT apply; current flow (spec approval → writing-plans) is correct |
| Plan already approved (no `needs-approval` label) | No action needed — plan is already approved |

**Evidence artifact:** `github_search_issues` response showing plan issues referencing the spec, and `github_issue_write` response confirming label removal and comment posting.

## Work State I/O

- **Reads from:** `## sub-issue-verification`
- **Writes to:** `## spec-to-plan-cascade`

After completing this task, write results to the work state file under section `## spec-to-plan-cascade` using the YAML format defined in `enforcement/work-state-schema.md`.