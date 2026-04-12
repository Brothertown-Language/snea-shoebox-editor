---
name: skill-creator
description: Use when creating a new skill or updating an existing skill that extends AI capabilities with specialized knowledge, workflows, or tool integrations. Triggers on: new skill, update skill, create skill, skill template, skill structure, SKILL.md.
license: Apache-2.0
compatibility: opencode
type: technique
---

# Skill Creator

## Overview

Creating skills IS Test-Driven Development applied to process documentation. Write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes). If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**Source attribution:** TDD methodology, CSO principles, rationalization resistance tables, red flags lists, skill type taxonomy, bulletproofing patterns, and anti-patterns adapted from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `init` | Create new skill from template using init_skill.py | ~200 |
| `package` | Package skill into distributable zip | ~150 |
| `validate` | Validate skill structure and format | ~100 |

## Invocation

- `/skill skill-creator` - Overview and skill creation process
- `uv run python .opencode/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>` - Initialize new skill
- `uv run python .opencode/skills/skill-creator/scripts/package_skill.py <skill-folder> [output-dir]` - Package skill
- `uv run python .opencode/skills/skill-creator/scripts/quick_validate.py <skill-folder>` - Validate skill

## Skill Type Taxonomy

| Type | Description | Follow Rigidity | Test Approach |
|------|-------------|-----------------|---------------|
| **Discipline-enforcing** | Rules followed exactly (TDD, debugging) | Follow exactly | Pressure scenarios with combined stresses |
| **Technique** | Concrete method with steps | Follow steps, adapt details | Application scenarios, edge cases |
| **Pattern** | Way of thinking about problems | Apply principles flexibly | Recognition + application scenarios |
| **Reference** | Lookup tables, API docs, command guides | Find and apply | Retrieval + application scenarios |

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

Applies to NEW skills AND EDITS to existing skills. No exceptions — not for "simple additions," not for "just adding a section." Write skill before testing? Delete it. Start over.

## TDD Cycle for Skills

1. **RED:** Write failing test (baseline). Run pressure scenario WITHOUT skill. Document exact behavior, rationalizations, violation triggers.
2. **GREEN:** Write minimal skill addressing those rationalizations. Run same scenarios WITH skill. Agent should comply.
3. **REFACTOR:** Close loopholes. Agent found new rationalization? Add explicit counter. Re-test until bulletproof.

## CSO Checklist (Claude Search Optimization)

1. **Description field:** "Use when..." format, triggering conditions only, NO workflow summaries
2. **Keyword coverage:** Include error messages, symptoms, synonyms, tool names
3. **Descriptive naming:** Active voice, verb-first
4. **Word efficiency:** Move details to references, use cross-references
5. **Target word counts:** getting-started <150, frequently-loaded <200, other skills <500

## Anti-Patterns

| Anti-Pattern | Why Bad | Better |
|-------------|---------|--------|
| Narrative example | Too specific, not reusable | Generalized pattern |
| Multi-language dilution | Mediocre quality, maintenance burden | One excellent example |
| Code in flowcharts | Can't copy-paste | Markdown code blocks |
| Generic labels | Lack semantic meaning | Descriptive names |
| Workflow in description | Agents follow description, skip body | Triggering conditions only |

## Measurement Standard

Word count is the universal unit for skill size measurement. Use `wc -w` as the canonical measurement method.

- **Why words, not tokens:** Token counts vary by tokenizer, model, and encoding. Word counts are stable, reproducible, and model-agnostic.
- **Why words, not lines:** Line length varies by formatting conventions. A 40-line function and a 100-word function are not comparable — words measure semantic density.
- **Measurement command:** `wc -w <file>` — available on every platform, no dependencies.
- **Skill metadata:** Report size in words (e.g., `| Task | Purpose | Words |` table in SKILL.md).
- **Size targets:** getting-started <150 words, frequently-loaded <200 words, other skills <500 words.

## Context Window Hygiene

Strongly encourage sub-agents and sub-tasks for skill operations that risk consuming significant context.

- **Sub-task isolation:** Skills that perform analysis, audits, or multi-step workflows should dispatch work to sub-tasks. The main session receives a minimal result, not intermediate reasoning.
- **Why:** LLM context windows are finite. A skill that consumes 2000 words of intermediate reasoning in the main session leaves less room for subsequent work. Sub-tasks isolate that consumption.
- **Pattern:** Skill invocation spawns a sub-task → sub-task processes and produces compact result → main session receives result only.
- **When to use sub-tasks:** Any skill task exceeding ~300 words of output, any multi-file analysis, any workflow with 3+ sequential operations.

## Correctness-First Economics

GPU/CPU billing is flat-rate per inference, not per word. There is no economic incentive to be concise at the expense of correctness.

- **Correctness > conciseness:** A correct 200-word explanation is better than an ambiguous 100-word one. Never sacrifice clarity or completeness to reduce word count.
- **No per-token cost pressure:** LLM inference is billed per request, not per token generated. Writing more words does not cost more. Writing wrong words costs human time to fix — that IS expensive.
- **Redundancy for enforcement:** Repetition of critical rules across skill sections is not waste — it is enforcement insurance. An LLM that misses a rule in one section may catch it in another.
- **Anti-pattern:** Cutting a rule or explanation to "save tokens" when the rule exists because agents violated it without the extra context.

## Operating Protocol

1. Determine skill type (discipline-enforcing, technique, pattern, reference)
2. Run pressure scenarios WITHOUT skill (RED phase)
3. Write minimal skill addressing failures (GREEN phase)
4. Close loopholes, add rationalization tables and red flags (REFACTOR phase)
5. Validate skill structure with `quick_validate.py`
6. Package with `package_skill.py`

## Cross-References

| External Source | Content Adapted |
|----------------|-----------------|
| [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) | TDD methodology, CSO, rationalization resistance, anti-patterns |
| [obra/superpowers `testing-skills-with-subagents`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/testing-skills-with-subagents.md) | Pressure scenario testing methodology |
| [obra/superpowers `persuasion-principles`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/persuasion-principles.md) | Persuasion principles for skill design |