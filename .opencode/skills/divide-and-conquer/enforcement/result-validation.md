# Result Validation Module

## Empty/Malformed/Overflow Result Handling

When `assemble-work` receives a sub-agent result, it MUST validate the result before recording it in the work state file.

### Validation Protocol

1. **Empty result**: Sub-agent returned no output at all
   - Action: FALLBACK to inline execution + report warning in chat
   - NEVER transition from empty result to silent halt

2. **Malformed result**: Result contract has invalid YAML or missing required fields
   - Action: Attempt to extract usable data from result
   - If extraction fails: FALLBACK to inline execution + report warning in chat
   - If extraction succeeds: Record what was extracted, note malformation

3. **Overflow result**: Sub-agent's context window exceeded during execution
   - Result will have `status: OVERFLOW`
   - Action: Invoke `overflow-signal.md` re-dispatch protocol
   - Split the overflowing task into smaller units and re-dispatch

### Required Result Contract Fields

Every sub-agent result MUST include:

| Field | Required | Type |
|-------|----------|------|
| `status` | Yes | `DONE \| DONE_WITH_CONCERNS \| BLOCKED \| OVERFLOW` |
| `task` | Yes | string (task name) |
| Other fields | Per task | Per result contract schema |

### Fallback Procedure

When inline fallback is attempted:
1. Report the original sub-agent failure to chat
2. Execute the sub-agent's task directly within the orchestration context
3. If fallback succeeds: continue work orchestration, note in work state
4. If fallback also fails: report double-failure, invoke `--task completion`, HALT