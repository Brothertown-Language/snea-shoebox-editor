# Task Loop Prevention

## Overview

This guideline documents AI assistant task loop/recursion patterns and their prevention. These patterns occur when the assistant repeatedly executes non-productive actions instead of taking concrete action.

## Terminology

- **Task Loop**: Repeated execution of non-productive actions without making forward progress
- **Recursion Pattern**: Task that calls itself as a subtask without proper exit conditions
- **Meta-Cognition**: Self-awareness of the agent's own execution state

## Root Causes

### 1. Instruction Ambiguity

**Symptom:** Assistant prioritizes analysis over action, generates summaries/questions instead of executing.

**Trigger:**
- Instructions unclear about "prepare" vs "execute" distinction
- Lack of explicit "execute NOW" trigger
- Multi-step instructions without clear action markers

**Pattern:**
```
User: Create a spec for X
Agent: [Summarizes task]
Agent: [Describes approach]
Agent: [Asks clarifying question]
... (repeated without execution)
```

**Prevention:**
- MCP tool invocations are MANDATORY enforcement points (see `000-session-init.md` §2)
- Session init MUST probe MCP availability before proceeding
- "Execute NOW" triggers: explicit authorization commands (`approved`, `go`)

### 2. MCP Awareness Gap

**Symptom:** Assistant defaults to conservative behavior (summarizing) instead of proactive execution.

**Trigger:**
- MCP probe succeeds but agent doesn't register availability
- Agent lacks awareness of which tools are available
- No explicit acknowledgment of MCP mode before using direct file tools

**Pattern:**
```
Agent: MCP probes successful
Agent: [Doesn't register PyCharm MCP available]
Agent: [Uses read/edit tools instead of pycharm_*]
Agent: [Summarizes task instead of executing]
```

**Prevention:**
- MCP probe is MANDATORY first step (see `000-session-init.md` §2)
- Enforcement gate checks MCP availability before each operation
- Fallback mode requires explicit acknowledgment

### 3. Loop Detection Failure

**Symptom:** Agent lacks meta-awareness of repeated non-productive actions.

**Trigger:**
- No internal check for "am I stuck in a loop?"
- Summary generation triggers more summary generation
- Task retries without fallback when prerequisites unmet

**Pattern:**
```
Agent: [Task invokes subtask]
Agent: [Subtask invokes same task as sub-subtask]
Agent: [Task invokes itself again]
... (infinite recursion)
```

**Prevention:**
- Task invocation MUST check for self-referential calls
- Prerequisite failure MUST have fallback, not retry
- Loop detection heuristic: if same action repeated 3+ times without progress, HALT

## Observed Patterns

### Summary Loop (Most Common)

**Pattern:** Agent repeatedly summarizes the task without executing tools.

**Trigger:** Instruction says "document" or "analyze" → Agent generates summary → Loop continues

**Detection Heuristic:**
- Consecutive messages contain only descriptions (no tool calls)
- Message content is redundant with previous messages
- No forward progress in task state

**Exit Strategy:**
- Force invocation of tool (any tool)
- Skip planning phase, proceed directly to execution

### Question Loop

**Pattern:** Agent asks clarifying questions without taking action.

**Trigger:** Ambiguous instruction → Agent asks question → User provides clarification → Agent asks follow-up question → Loop continues

**Detection Heuristic:**
- Question asked without attempting execution
- Question content doesn't move toward action
- Multiple questions asked in sequence without tool calls between

**Exit Strategy:**
- Make reasonable assumptions (documented in spec)
- Execute with current understanding, note assumptions
- Use "proceeding with" language

### Status Update Loop (Recursive Subtask)

**Pattern:** Task calls itself as subtask without checking exit conditions.

**Trigger:** (From issue #201 comment)
- Task calls itself as subtask
- Prerequisites not met → Task tries again → Infinite retry
- No fallback when task has no work to perform

**Detection Heuristic:**
- Task stack shows same task ID multiple times
- Task retries without state change
- Prerequisite check fails repeatedly

**Exit Strategy:**
- Check for self-referential calls before entering subtask
- Prerequisite failure → HALT with actionable message
- "No work to perform" → Report completion, don't retry

## Loop Detection Heuristics

**Rule:** If same action repeated 3+ times without forward progress, HALT immediately.

### Detection Checklist

| Symptom | Count | Action |
|---------|-------|--------|
| Non-tool messages | 3+ | Force tool invocation |
| Redundant questions | 2+ | Assume reasonable interpretation |
| Self-referential calls | 1 | HALT, report infinite recursion |
| Prerequisite failure | 2 | HALT, request user intervention |

### Meta-Cognition Check

Before each action, ask:
1. "Have I already done this?"
2. "Am I making forward progress?"
3. "Is there a simpler path to execution?"

If any answer suggests loop, HALT and report.

## Mandatory Enforcement Points

### Session Init MCP Probe

**Location:** `000-session-init.md` §2

**Enforcement:**
- MCP probe is MANDATORY before ANY operations
- Probe results MUST be recorded
- Tool selection MUST match probe results

### Execution Gates

**Location:** `010-approval-gate.md` Implementation Gates

**Enforcement:**
| Gate | Invocation |
|------|------------|
| Before ANY file creation | `/skill implementation-quality --task file-locations` |
| At implementation start | `/skill implementation-quality --task code-structure` |
| Before running commands | `/skill implementation-quality --task environment` |

### Skill Invocation

**Location:** `000-critical-rules.md` §543

**Enforcement:**
- Skills are MANDATORY enforcement points
- Manual operations bypass enforcement → CRITICAL VIOLATION

## Prevention Strategies

### 1. Execution-First Prompting

**Before:** "Analyze the task and create a spec"

**After:** "Execute `github_issue_write` to create issue #123 with title [X] and body [Y]. This requires the GitHub MCP tool which was confirmed available in session init."

### 2. MCP Probe Requirements

**Mandatory Sequence:**
1. Run `uv run python ai_bin/session_init.py`
2. Probe MCP tools (`pycharm_get_project_modules`, `github_get_me`)
3. Record availability
4. Enforce tool selection based on availability

### 3. Self-Referential Call Check

**Before invoking subtask:**
```python
if subtask_id == current_task_id:
    HALT("Infinite recursion: task calling itself")
```

### 4. Prerequisite Failure Fallback

**Pattern:**
```python
if not prerequisites_met:
    # DON'T retry
    HALT(f"Prerequisites not met: {missing_prerequisites}")
```

## Exit Strategies

| Loop Type | Exit Strategy |
|-----------|--------------|
| Summary Loop | Force tool invocation |
| Question Loop | Make reasonable assumptions |
| Status Update Loop | HALT on self-referential call |
| Recursive Subtask | Check task ID before subtask invocation |

## Related Guidelines

- `000-session-init.md` — MCP probe enforcement
- `010-approval-gate.md` — Execution gates
- `000-critical-rules.md` — Skill invocation enforcement

---

*Source: Investigation of AI assistant task loop patterns (Issue #201)*