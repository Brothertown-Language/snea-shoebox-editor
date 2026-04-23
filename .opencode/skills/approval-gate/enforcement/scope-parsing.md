# Scope Parsing Module

## Verb-Prefix Parsing Table

Authorization phrases carry implicit scope — the pipeline stage the developer expects work to reach. Parse authorization text for scope qualifiers:

| Phrase Pattern | Scope | HALT After | Gap-Fill | PR Strategy |
|----------------|-------|------------|----------|-------------|
| `"approved #N"` (no qualifier) | standard | review-prep | None | individual |
| `"approved #N for spec"` or `"#N approved for spec"` | for_spec | spec_created | None | none |
| `"approved #N for plan"` or `"#N approved for plan"` | for_plan | plan_created | auto-create spec | none |
| `"approved #N for implementation"` or `"#N approved for implementation"` | for_implementation | implementation_complete | auto-create spec+plan, auto-approve | individual |
| `"approved #N for code review"` or `"#N approved for code review"` | for_code_review | code_review_ready | auto-create spec+plan, auto-approve | individual |
| `"approved #N to PR"` or `"#N approved to PR"` | for_pr | pr_created | auto-create spec+plan, auto-approve, auto-PR | stacked |
| `"approved #N pr only"` or `"#N approved for pr only"` | pr_only | pr_created | None | stacked |
| `"approved #N for review"` or `"#N approved for review only"` | review_only | code_review_ready | None | individual |
| `"approved for next phase"` or `"approved #N for next phase"` | for_next_phase | next_phase_complete | auto-approve next phase | individual |
| `"approved for phase N"` or `"approved #N for phase N"` | for_phase_N | phase_N_complete | auto-approve up to phase N | individual |

## "Next Phase" Resolution

When scope resolves to `for_next_phase`, the agent MUST:

1. **Read the spec/plan body** to identify phase structure (look for `### Phase N:` or `#### Task N:` headings)
2. **Identify completed phases** by checking sub-issue state (`get_sub_issues`) and verifying merged PRs for each
3. **Resolve to the next sequential uncompleted phase number**
4. **Set `halt_at`** to `phase_N_complete` where N is the resolved next phase
5. **Set gap-fill** to `auto-approve` for that specific phase only

### Resolution Logic

```python
def resolve_next_phase(issue_num, issue_body):
    """
    Resolve 'next phase' to a specific phase number based on
    current completion state.
    """
    sub_issues = github_issue_read(
        method="get_sub_issues", issue_number=issue_num
    )

    phase_pattern = re.compile(r"(?:###?\s*Phase\s+(\d+)|####\s*Task\s+(\d+))")
    phases_in_body = phase_pattern.findall(issue_body)

    completed_phases = set()
    for sub in sub_issues:
        sub_detail = github_issue_read(
            method="get", issue_number=sub["number"]
        )
        if sub_detail.get("state") == "closed":
            prs = github_search_pull_requests(
                query=f"Fixes #{sub['number']} repo:{OWNER}/{REPO}"
            )
            for pr in prs:
                pr_detail = github_pull_request_read(
                    method="get", owner=OWNER, repo=REPO,
                    pullNumber=pr["number"]
                )
                if pr_detail.get("merged_at") is not None:
                    phase_match = re.search(
                        r"[Pp]hase\s+(\d+)", sub_detail.get("title", "")
                    )
                    if phase_match:
                        completed_phases.add(int(phase_match.group(1)))

    all_phases = sorted(set(
        int(p[0]) for p in phases_in_body if p[0]
    ))
    if not all_phases:
        all_phases = list(range(1, len(sub_issues) + 1))

    next_phase = None
    for p in all_phases:
        if p not in completed_phases:
            next_phase = p
            break

    if next_phase is None:
        return {
            "resolved_scope": "standard",
            "halt_at": "review_prep",
            "reason": "All phases already completed",
        }

    return {
        "resolved_scope": "for_phase_N",
        "halt_at": f"phase_{next_phase}_complete",
        "phase_number": next_phase,
        "gap_fill": f"auto-approve phase {next_phase}",
    }
```

### "Approved for Phase N" Resolution

When scope resolves to `for_phase_N`:

```python
def resolve_phase_n(phase_number, total_phases):
    """
    Resolve 'approved for phase N' to halt_at and gap-fill values.
    """
    is_final = (phase_number == total_phases)

    return {
        "resolved_scope": "for_phase_N",
        "halt_at": f"phase_{phase_number}_complete",
        "phase_number": phase_number,
        "gap_fill": f"auto-approve up to phase {phase_number}",
        "is_final_phase": is_final,
        "pr_strategy": "individual" if not is_final else "individual",
    }
```

| Phase Context | halt_at | Gap-Fill | PR Strategy |
|---------------|---------|----------|-------------|
| Phase N is intermediate | `phase_N_complete` | Auto-approve phases 1 through N | individual |
| Phase N is final | `review_prep` (standard completion) | Auto-approve all phases | individual |

**⚠️ CRITICAL: `for_next_phase` and `for_phase_N` scopes do NOT cascade to subsequent phases.** Authorization for "next phase" covers exactly that one phase. Authorization for "phase 2" covers phases 1–2 only. Subsequent phases require separate authorization.

## Scope Derivation Rules

1. **No qualifier = standard**: `"approved #1200"` → `standard` scope, review-prep halt, no gap-fill
2. **Qualifier present = parse**: Match phrase against table above; ambiguous phrases default to standard
3. **Multiple issues**: `"approved #1200 #1201 #1197 for implementation"` → `for_implementation` scope applies to all listed issues
4. **Phase qualifier**: `"approved: Phase 1 only"` → single-phase authorization for the named phase only, then HALT
5. **"Next phase" resolution**: `"approved #N for next phase"` → resolve via `resolve_next_phase()` which reads spec/plan body, identifies completed phases (via merged PRs and STATUS markers), and sets halt_at to the next sequential uncompleted phase
6. **"Phase N" resolution**: `"approved #N for phase N"` → resolve via `resolve_phase_n()` which sets halt_at based on whether the phase is intermediate or final

## PR Strategy Map

| Scope | PR Strategy |
|-------|-------------|
| standard | individual (one PR per issue) |
| for_spec | none |
| for_plan | none |
| for_implementation | individual |
| for_code_review | individual |
| for_pr | stacked |
| pr_only | stacked |
| review_only | individual |
| for_next_phase | individual |
| for_phase_N | individual |