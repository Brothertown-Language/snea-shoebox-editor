# Task: verify-authorization — Step 5c: Scope-Aware Gap-Fill Cascade

## Purpose

When `authorization_scope` from Step 2.0 is >= `for_plan`, missing intermediate artifacts are gap-filled automatically. This eliminates the "catch-22" where pipeline authorization says "go to PR" but the plan doesn't exist yet — the scope horizon authorizes its creation.

## 5c.1 Detect Scope Horizon

```python
SCOPE_HORIZON = {
    "standard":         "review_prep",
    "for_spec":         "spec_created",
    "for_plan":         "plan_created",
    "for_implementation": "implementation_complete",
    "for_code_review":  "code_review_ready",
    "for_pr":           "pr_created",
    "pr_only":          "pr_created",
    "review_only":      "code_review_ready",
}

# From Step 2.0 result
scope = verification_result["authorization_scope"]
halt_at = SCOPE_HORIZON[scope]
```

## 5c.2 Gap-Fill Actions by Scope

```python
GAP_FILL = {
    "for_spec": [],  # Spec is the target; no upstream gap
    "for_plan": ["auto_create_spec"],  # Missing spec is gap-filled
    "for_implementation": ["auto_create_spec", "auto_create_plan", "auto_approve_plan"],
    "for_code_review": ["auto_create_spec", "auto_create_plan", "auto_approve_plan"],
    "for_pr": ["auto_create_spec", "auto_create_plan", "auto_approve_plan", "auto_create_pr"],
    "pr_only": [],  # Assumes branch exists; no gap-fill
    "review_only": [],  # Assumes code exists; no gap-fill
    "standard": [],  # No gap-fill; all artifacts must pre-exist
}
```

## 5c.3 Execute Gap-Fill

```python
def execute_gap_fill(scope, issue_number, issue_labels, issue_title):
    """Auto-create missing artifacts when scope authorizes it."""
    actions = GAP_FILL.get(scope, [])
    results = []

    if "auto_create_spec" in actions:
        # Check if spec already exists
        is_spec = "spec" in [l["name"] for l in issue_labels] or issue_title.startswith("[SPEC")
        if not is_spec:
            # Invoke brainstorming --task explore to create spec
            results.append({"action": "auto_create_spec", "status": "dispatched", "target": "brainstorming"})
        else:
            results.append({"action": "auto_create_spec", "status": "skipped", "reason": "spec_exists"})

    if "auto_create_plan" in actions:
        # Check if plan already exists
        is_plan = "plan" in [l["name"] for l in issue_labels] or issue_title.startswith("[PLAN]")
        if not is_plan:
            # Invoke writing-plans --task create to create plan
            results.append({"action": "auto_create_plan", "status": "dispatched", "target": "writing-plans"})
        else:
            results.append({"action": "auto_create_plan", "status": "skipped", "reason": "plan_exists"})

    if "auto_approve_plan" in actions:
        # Cascade approval already handled by Step 5b for existing plans
        # For gap-filled plans, writing-plans auto-approves when scope >= for_plan
        results.append({"action": "auto_approve_plan", "status": "delegated", "target": "writing-plans"})

    if "auto_create_pr" in actions:
        # PR creation is handled by git-workflow scope awareness after implementation
        results.append({"action": "auto_create_pr", "status": "deferred", "target": "git-workflow"})

    return results
```

## 5c.4 PR Strategy Determination

PR strategy is derived from scope, NOT from issue count. See `enforcement/auto-dispatch-table.md` for the complete PR strategy mapping.

## Gap-Fill Precedence Principle (Step 5b.5)

**Before evaluating any blocking gate in Steps 5 through 5c, the agent MUST apply this precedence principle:**

> When `authorization_scope`'s gap-fill actions cover a missing artifact requirement, that requirement is a gap-fill trigger, not a blocking gate. Hard gates only apply to artifacts outside the scope's gap-fill coverage.

**Application to Bug Reports:**

The critical rule "Bug Reports Without Fix Spec" requires a fix-spec sub-issue before implementation. When `authorization_scope >= for_implementation` (which includes `for_implementation`, `for_code_review`, and `for_pr`), the gap-fill actions include `auto_create_spec`. This means:

- **Missing fix-spec for a bug report + `for_pr` authorization** → Gap-fill trigger: proceed to Step 5c. NOT a blocking gate.
- **Missing fix-spec for a bug report + `for_implementation` authorization** → Gap-fill trigger: same as above. NOT a blocking gate.
- **Missing fix-spec for a bug report + `for_code_review` authorization** → Gap-fill trigger: same as above. NOT a blocking gate.
- **Missing fix-spec for a bug report + `for_plan` authorization** → Gap-fill trigger: `for_plan` includes `auto_create_spec`. NOT a blocking gate.
- **Missing fix-spec for a bug report + `for_spec` authorization** → Gap-fill trigger: `for_spec` targets spec creation. NOT a blocking gate.
- **Missing fix-spec for a bug report + `standard` authorization** → Blocking gate: `standard` scope has NO gap-fill actions, so the fix-spec must already exist. HALT and report missing fix-spec.

**Evidence artifact:** The agent's verification report MUST note when a blocking gate was overridden by the Gap-Fill Precedence Principle, citing the specific gate, the missing artifact, and the covering gap-fill action.