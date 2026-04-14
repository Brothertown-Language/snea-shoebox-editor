# OpenCode Changelog

All notable changes to the `.opencode/` directory (skills, guidelines, agent configuration) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - Unreleased

### Changed

- **Audit auto-fix exemption** (#793, absorbs #806) - Add exemption in `000-critical-rules.md` and `010-approval-gate.md` allowing spec-auditor auto-fix classified findings to be applied directly to GitHub Issues without separate authorization. Conditional fixes still require auth; flag-for-review findings are reported only. Add cross-reference in `spec-auditor/SKILL.md`.
- **Todowrite lifecycle mandate** (#803, fixes #801) - Add critical violation for stale todowrite state in `000-critical-rules.md`. Add CREATE/UPDATE/CLEAR lifecycle rules in `060-tool-usage.md` §7. Add cleanup checklist item in `finishing-a-development-branch` and verification step in `verification-before-completion`.
- **Autonomous structural decisions** (#807, fixes #804) - Add critical violation for pushing agent intelligence decisions to users in `000-critical-rules.md`. Add autonomous structural classification rule in `brainstorming/tasks/explore.md` with ask/don't-ask criteria. Add "Structural decisions are agent-resolved" principle to brainstorming SKILL.md.
- **Programming principles in spec-auditor** (#791) - Add `principles` subtask to `spec-auditor` checking documents against 20 engineering principles with 8 problem classes (SRP_VIOLATION, SOC_VIOLATION, YAGNI_VIOLATION, KISS_VIOLATION, COUPLING_VIOLATION, BLAST_RADIUS_VIOLATION, TESTABILITY_VIOLATION, PRINCIPLE_VIOLATION). Add bidirectional cross-references across 5 auditing skills.
- **Spec/plan boundary enforcement** (#792) - Add `PLAN-BLEED` auto-fix problem class to spec-auditor. Add boundary check step in spec-creation write task. Replace "API contracts"/"Data contracts" with "Interface Requirements"/"Data Boundaries" in decompose task. Add boundary note to spec templates. Flag "Implementation" phase names as potential plan-bleed in concern-separator.
- **Code inspection checklist** (#818) - Create `015-pre-spec-inspection.md` guideline with 6-item mandatory checklist (trace call paths, verify imports, detect dead code, verify format/protocol assumptions, confirm architectural layer, check for existing alternatives). Add as mandatory Step 0 in brainstorming explore task and pre-condition in spec-creation. Strengthen "Spec Without Investigation" critical violation with checklist reference.
- **Uniform batch workflow** (#729) - Unify `batch-orchestrate` and `batch-execution` into a consistent branch-per-issue pattern with merge-based dependency resolution. Remove single-issue dispatch edge case. Replace `prior_results` change templates with AI-composed `prior_context` (intent-and-context). Add `BASE_BRANCH` parameter to `create-worktree` for batch workflows. Add frozen branches rule and conflict resolution tier protocol during dependency merges. Add batch assembly with squash-merge into single PR.
- **Compare URL base branch** (`approval-gate/tasks/post-implementation.md`, `git-workflow/tasks/review-prep.md`) - Fix feature branch compare URLs from `compare/main` to `compare/dev` to match the three-branch model
- **Authorization cascade rules** (`approval-gate/SKILL.md`, `000-critical-rules.md`, `010-approval-gate.md`) - Add Reference ≠ Authorization Cascade rule requiring formal sub-issue links, not text references, for authorization cascade. Add Confirmation ≠ Authorization rule distinguishing observation confirmations from implementation authorization.
- **Session init plugin** (#710, #720) - Anti-hallucination context: Remote URL, worktree detection paths, hooks path, in-worktree awareness
- **Session init uvx compatibility** (#721) - Proper shebang, pyproject.toml entry point, uvx invocation
- **env-loader worktree documentation** (#723) - Document input.$ cwd behavior for worktree sessions
- **Skill-creator principles** (#711) - Add Measurement Standard (word counts), Context Window Hygiene (sub-agent encouragement), Correctness-First Economics (flat-rate billing) to skill-creator SKILL.md and init template. Propagate word-count measurement to code-size-enforcement, coherence-auditor, fragment-manager, git-workflow, guideline-auditor.
- **Markdown formatting enforcement** (#731) - Apply mdformat with full plugin stack (frontmatter, tables, config, GFM) in read-only mode across all guidelines and skills. Repair damaged ordered-list enumerations and normalize markdown structure in 73 files. Add `--number --compact-tables` flags and plugin-based `--check` command to AGENTS.md.
