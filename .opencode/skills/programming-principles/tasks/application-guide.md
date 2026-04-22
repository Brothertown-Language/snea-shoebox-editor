# Task: application-guide

## Purpose

How to apply the 20 principles during design, implementation, and review. Includes context-prioritization table, red flags, and tradeoff justification format.

## Entry Criteria

- About to design, implement, or review code
- Need guidance on which principles to prioritize

## Exit Criteria

- Principles correctly prioritized for the current context
- Tradeoffs documented where principles are relaxed

## Procedure

### During Design (Pre-Implementation)

1. Scan the 20 principles before designing a new module, function, or API
2. Identify which principles apply strongly to the current context
3. Document deliberate relaxations as tradeoff notes in the spec or design doc
4. Don't over-apply — not every function needs all 20 principles considered

### During Implementation (Active Coding)

1. When writing a function or class, check principles 1–3 (KISS, DRY, SRP) as a fast triage
2. When designing interfaces or module boundaries, check principles 4–8 (SoC, cohesion, information hiding, Demeter, composition)
3. When considering "should I add this?", check YAGNI first
4. When encountering a bug or edge case, check Fail Fast and Defensive Programming
5. When the code feels fragile, check Deterministic Behavior, Idempotence, and Blast Radius

### During Review

1. Look for principles violated without documented tradeoff notes — these are the real issues
2. Don't flag well-documented tradeoffs — the author already made a conscious decision
3. Focus on principles that apply strongly in the current context — not all 20 every time

### Quick Reference: Principles by Context

Not all 20 principles matter equally in every context. Use this table to prioritize:

| Context | Prioritize | Relax |
| -- | -- | -- |
| One-off scripts | KISS, Fail Fast | SRP, SoC, Observability, Blast Radius |
| Public APIs | Info Hiding, SoC, Defensive Programming, CQS | Performance optimizations |
| Business logic | SRP, DRY, Determinism, Testability | Premature abstraction |
| Concurrency | Minimize Mutable State, Idempotence, Fail Fast | DRY (lock patterns may need duplication) |
| Data pipelines | Idempotence, Observability, Defensive Programming | CQS (side effects are inherent) |
| Prototypes/MVPs | KISS, YAGNI | SoC, Defensive Programming, Observability |

### Red Flags — When to Pause and Reconsider

| Thought | Check |
| -- | -- |
| "This function is getting long" | SRP, KISS — should it be decomposed? |
| "I need this in three places" | DRY — is it truly the same, or coincidental duplication? |
| "Let me add this just in case" | YAGNI — is there a current requirement? |
| "They'll probably need this later" | YAGNI — build when needed, not when imagined |
| "This call chain is convenient" | Law of Demeter — does it create fragile coupling? |
| "I'll make this configurable" | Explicitness, YAGNI — is there a current need? |
| "It works on my machine" | Deterministic Behavior — what makes it nondeterministic? |
| "We can add logging later" | Observability First — design it in now |
| "This is a quick fix" | Blast Radius — what breaks if it's wrong? |
| "I'll skip validation here" | Defensive Programming — is this truly an internal caller? |

### Tradeoff Justification Format

When deliberately relaxing a principle, document it:

```
PRINCIPLE RELAXED: [Principle Name]
REASON: [Why the cost of following exceeds the benefit here]
ALTERNATIVE CONSIDERED: [What following the principle would look like]
ACCEPTANCE CRITERIA: [When this relaxation should be revisited]
```

**Example:**

```
PRINCIPLE RELAXED: Single Responsibility Principle
REASON: This 8-line function coordinates validation and persistence, which change together for this entity. Splitting adds 3 classes for what is effectively one operation.
ALTERNATIVE CONSIDERED: Separate Validator and Repository classes with a Coordinator
ACCEPTANCE CRITERIA: Revisit if validation rules grow beyond 5 or if persistence logic becomes independent
```
