# Completion Checkpoint Module

## Sub-Agent Completion Detection

Each sub-agent dispatched by `assemble-work` MUST produce a result contract upon completion. The completion checkpoint determines whether the sub-agent's work is verifiably complete.

### Completion Detection Protocol

1. **Result contract received**: Sub-agent returns YAML result contract with `status` field
2. **Status check**: `status` must be `DONE` or `DONE_WITH_CONCERNS`
3. **Concerns check**: If `DONE_WITH_CONCERNS`, log concerns but do not block
4. **Failure check**: If `OVERFLOW` or `BLOCKED`, initiate recovery mode

### Status Classification

| Status | Meaning | Action |
|--------|---------|--------|
| `DONE` | All sub-tasks completed successfully | Record result, proceed to next sub-agent |
| `DONE_WITH_CONCERNS` | Completed but with warnings | Record concerns in work state, proceed |
| `BLOCKED` | Cannot proceed due to external dependency | HALT, report blocker in chat |
| `OVERFLOW` | Context window exceeded during execution | Initiate overflow recovery |

### Recovery Mode

When a sub-agent fails:
1. Log the failure in work state file
2. Attempt inline fallback (perform the sub-agent's task directly)
3. If inline fallback succeeds: continue work orchestration
4. If inline fallback fails: report double-failure, invoke `--task completion`, HALT with status message
5. NEVER silently continue after sub-agent failure