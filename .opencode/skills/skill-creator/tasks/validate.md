# Validate

Agent-driven semantic review workflow for skill card validation. Triggered when a developer requests "validate skill cards", "review skills", "skill card review", or similar phrasing. The validation script (`validate_skill_cards.py`) serves as a sensor that detects mechanical violations; the agent is the actor that interprets findings, resolves semantic issues, and applies corrections.

## Two Tiers of Invocation

There are two tiers of invocation depending on what the developer needs.

The default tier is script-only validation. Running `uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py` performs fast mechanical checks against REQ-1 (frontmatter fields), REQ-2 (CSO description format), and REQ-3 (worktree mode section). This tier is used during the enforcement test pipeline and for quick validation when the developer wants a fast read on skill card health.

The second tier is full review, which layers agent-driven semantic analysis on top of the mechanical checks. This tier is triggered when the developer explicitly requests skill card validation or a skill review — phrases like "validate skill cards", "review skills", or "skill card review". The full review runs the script first, then the agent performs its own analysis across all skill cards in the repository.

## Phase 1: Script Validation

The agent begins by running `uv run .opencode/skills/skill-creator/scripts/validate_skill_cards.py` and collecting the output. This identifies which skills fail mechanical REQ-1/2/3 checks and how. The script output is parsed to build a working list of mechanically-failing skills that need content-level attention in Phase 2. Skills that pass mechanical checks still proceed to Phases 3 through 5 for cross-skill and within-skill semantic analysis.

When using `--json` for programmatic consumption, the JSON array contains objects with fields: `skill_name`, `file_path`, `violation_type`, `rule_id`, `message`, `detail`, `line_approx`.

## Phase 2: Content and Intent Analysis for Failing Skills

For each skill that failed mechanical validation, the agent reads the full SKILL.md content and understands the skill's purpose, operations, and triggering conditions before writing any corrections. This is not a search-and-replace exercise — each fix must reflect what the skill actually does.

CSO descriptions are the most common mechanical failure. The fix is not to prepend "Use when" to an existing noun phrase like "Skill-creator" or "Git-workflow". Instead, the agent reformulates the description as a proper sentence that captures the skill's triggering conditions: "Use when creating a new skill or updating an existing skill that extends AI capabilities with specialized knowledge, workflows, or tool integrations." The triggering conditions come from reading the skill, not from pattern-matching the old description.

Worktree mode sections fail REQ-3 when they are missing or generic. The agent writes a section that reflects the skill's specific operations in a worktree context. For example, `git-workflow` discusses branch operations and how branch targets change when working in a worktree, while `notebook-operations` discusses Jupyter file path handling and why notebook operations must target the worktree path. A generic boilerplate section like "This skill operates in worktrees by using worktree.path" signals that the agent did not read the skill.

Placeholder substitutions handle hardcoded identity values. Attribution lines use the canonical format `Co-authored with AI: <AgentName> (<ModelId>)`. Other prose uses angle-bracket placeholders: `<github.owner>`, `<github.repo>`, `<dev.name>`, and so on. The agent replaces hardcoded values with the appropriate placeholder based on context — attribution lines follow one format, prose references follow another.

Missing frontmatter fields receive values drawn from the skill's actual content. The `type` field matches the skill's type per the taxonomy — `discipline-enforcing` for skills that constrain agent behavior, `workflow` for skills that define procedural sequences, `utility` for helper tools — not a default value applied uniformly.

## Phase 3: Cross-Skill Conflict Detection Across All Skills

This phase reads every SKILL.md in the repository, not just the mechanically-failing ones. The agent looks for four categories of cross-skill conflict.

First, two skills giving contradictory instructions for the same scenario. If one skill says "always create a worktree first" and another skill's operating protocol assumes the working directory is the main repo, that contradiction will produce inconsistent agent behavior depending on which skill loads first.

Second, overlapping trigger keywords without differentiation. If two skills both trigger on the word "plan", the agent must be able to determine which skill applies from context — or the trigger keywords need to be narrowed so that ambiguity is resolved.

Third, cascading references forming cycles. If skill A's operating protocol references skill B, and skill B's protocol references skill A, the agent may loop or fail to terminate. Cycles must be broken by making one direction authoritative and the other a soft reference.

Fourth, contradictory enforcement rules for the same context. If one skill says "HALT on missing approval" and another says "proceed if authorization scope covers it", the agent needs to know which rule takes precedence for that specific context.

## Phase 4: Within-Skill Conflict Detection Across All Skills

For each individual skill, the agent checks for internal consistency.

An overview section that contradicts the task body or operating protocol is a within-skill conflict. If the overview says "this skill never modifies files" but a task body describes file-editing steps, the overview or the task body is wrong, and the developer must decide which.

A frontmatter `type` field that does not match the skill's actual structure is another within-skill conflict. A skill labeled `discipline-enforcing` that contains only workflow steps without enforcement rules is misclassified.

Enforcement rules that conflict with the operating protocol create ambiguity about what the agent should do when both apply. The agent flags these and waits for the developer to specify which takes precedence.

Cross-references to non-existent files or tasks — a MISSING-TRACEABILITY finding — indicate that the skill's structure has drifted from its documentation. The agent reports the broken reference and the expected target.

## Phase 5: Ambiguity Detection Across All Skills

For each skill, the agent scans for vague or underspecified language that could produce inconsistent agent behavior.

Vague trigger phrases like "when appropriate" or "if needed" give no guidance on when the skill should be invoked. The agent reports the ambiguous phrase and asks the developer to sharpen it.

Underspecified enforcement rule conditions create the same problem. An enforcement rule that says "halt on error" without specifying what counts as an error will produce different halting behavior depending on the agent's interpretation.

Ambiguous authorization language — phrases that could be read as either requiring or merely permitting an action — must be clarified so that the agent's behavior is deterministic.

Missing edge cases in enforcement rules leave the agent without guidance when uncommon situations arise. The agent reports the gap and the edge case that exposed it.

## Phase 6: Presenting Findings

Findings are presented to the developer one at a time, not as a bulk report. This allows the developer to consider each finding individually without being overwhelmed.

Auto-fixable findings — wrong placeholder values, missing frontmatter fields with unambiguous correct values — are applied by the agent immediately. The agent confirms each fix with the developer before moving on.

Conflicts — contradictory rules across skills or within a skill — are presented with the contradiction described in plain language. The agent asks the developer which rule or interpretation should govern, and waits for a response before proceeding. The agent does not resolve conflicts autonomously because the resolution may depend on project priorities or architectural intent that only the developer can assess.

Ambiguities — vague triggers, underspecified conditions, missing edge cases — are presented with the problematic language quoted and the ambiguity explained. The agent asks the developer to clarify and waits for a response. The agent does not sharpen ambiguous language on its own because the correct specificity depends on the developer's intent for the skill.

This separation between auto-fixable findings and findings requiring developer feedback is important. Mechanical violations have objectively correct fixes — a missing `type` field has a value determined by the skill's content, a wrong placeholder has a correct substitution. Semantic conflicts and ambiguities do not have objectively correct resolutions; they require judgment about project intent, and that judgment belongs to the developer.