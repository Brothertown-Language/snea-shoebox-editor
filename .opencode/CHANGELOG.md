# OpenCode Changelog

All notable changes to the `.opencode/` directory (skills, guidelines, agent configuration) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - Unreleased

### Changed

- **Compare URL base branch** (`post-implementation.md`, `implementation-workflow/SKILL.md`) - Fix feature branch compare URLs from `compare/main` to `compare/dev` to match the three-branch model
- **Authorization cascade rules** (`approval-gate/SKILL.md`, `000-critical-rules.md`, `010-approval-gate.md`) - Add Reference ≠ Authorization Cascade rule requiring formal sub-issue links, not text references, for authorization cascade. Add Confirmation ≠ Authorization rule distinguishing observation confirmations from implementation authorization.
- **Session init plugin** (#710, #720) - Anti-hallucination context: Remote URL, worktree detection paths, hooks path, in-worktree awareness
- **Session init uvx compatibility** (#721) - Proper shebang, pyproject.toml entry point, uvx invocation
- **env-loader worktree documentation** (#723) - Document input.$ cwd behavior for worktree sessions
- **Skill-creator principles** (#711) - Add Measurement Standard (word counts), Context Window Hygiene (sub-agent encouragement), Correctness-First Economics (flat-rate billing) to skill-creator SKILL.md and init template. Propagate word-count measurement to code-size-enforcement, coherence-auditor, fragment-manager, git-workflow, guideline-auditor.
