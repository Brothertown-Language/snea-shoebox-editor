---
name: programming-principles
description: Use when designing functions, classes, or modules; writing or reviewing implementation code; making architecture decisions; or evaluating tradeoffs between competing approaches. Triggers on: design, implement, refactor, architecture, tradeoff, principle, KISS, DRY, SRP, coupling, cohesion, YAGNI.
type: pattern
license: MIT
compatibility: opencode
---

# Programming Principles

## Overview

20 engineering principles as the **single authoritative source** for design judgment and enforcement rules. Each principle includes both the hard rule (where applicable) and the judgment context (when to apply strongly, when to relax). Other files reference HERE — never the other direction.

**Core ethic: Intelligent judgment, not dogmatism.** Principles are tools, not commandments. Apply them where they improve outcomes; relax them where the cost exceeds the benefit — but always document the tradeoff.

## Relationship to Code Standards

| This Skill | `080-code-standards.md` |
|------------|--------------------------|
| Master source for all 20 principles (rules + judgment) | Project-specific conventions (pathlib, f-strings, no re-exports, numbering, etc.) |
| Both enforcement AND design judgment | Principles REMOVED from here; cross-reference note points to this skill |
| Applies to any codebase | Applies to this repo only |

## How to Apply These Principles

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

### Invocation

This skill is **reference-driven**, not dispatch-triggered. Load via `/skill programming-principles` when the agent needs design judgment.

| When to Invoke | Example Trigger |
|----------------|-----------------|
| During design decisions | "Which approach has better cohesion?" |
| Before implementation | "Am I violating any principles here?" |
| During code review | "This violates CQS — is the tradeoff documented?" |
| When evaluating alternatives | "Option A has lower coupling but Option B is simpler" |

---

## The 20 Principles

### 1. KISS — Keep It Simple, Stupid

**Core idea:** Prefer the simplest working solution. Avoid cleverness.

**Enforcement:** "Simplest correct solution. No unnecessary abstraction or cleverness." (Also enforced in `080-code-standards.md`)

**Apply strongly when:**
- Writing business logic that others must understand
- Multiple approaches solve the problem equally well
- Code has high churn or frequent reader turnover

**Relax when:**
- Performance-critical paths where cleverness is measurably faster
- Domain-specific algorithms where "simple" means "deceptively wrong" (e.g., date handling, concurrency)

**Tradeoff note:** "Using [approach] instead of simpler alternative because [measurable reason]."

---

### 2. DRY — Don't Repeat Yourself

**Core idea:** No duplicated logic. Extract shared abstractions only when justified by three or more instances.

**Enforcement:** "No duplicated logic. Extract shared functionality into reusable functions/modules. If you copy-paste code, you're doing it wrong." (Also enforced in `080-code-standards.md`)

**Apply strongly when:**
- Identical logic appears in 3+ places
- Bug fixes require changes in multiple locations

**Relax when:**
- Two instances of similar-but-not-identical logic (premature abstraction)
- Duplication is accidental and each instance may diverge
- The "shared" abstraction would couple unrelated domains

**Tradeoff note:** "Keeping duplicated logic in [module_a] and [module_b] because [reason they may diverge or coupling cost]."

---

### 3. Single Responsibility Principle

**Core idea:** Each function, class, or module does exactly one thing.

**Enforcement:** "Every function/method performs exactly ONE task. If a function has multiple responsibilities, split it. Decompose ALL tasks, plans, and algorithms into discrete single-function methods." (Also enforced in `080-code-standards.md` as "Single Function Methods" and "No Monoliths")

**Apply strongly when:**
- A function has multiple reasons to change
- Testing requires mocking unrelated dependencies
- A class name contains "and" or "or" (e.g., `ParserAndValidator`)

**Relax when:**
- Trivially small functions where splitting adds indirection without clarity
- Adapter/facade patterns that intentionally coordinate multiple concerns
- Data transfer objects that group related fields

**Tradeoff note:** "[class/function] handles [concern A] and [concern B] because [reason they must change together or are too small to separate]."

---

### 4. Separation of Concerns

**Core idea:** Keep domains isolated. UI ≠ business logic ≠ data access.

**Enforcement:** "Non-Monolithic: Break large blocks into cohesive, independent components." (Also enforced in `080-code-standards.md` as "Non-Monolithic" and in `concern-separation-auditor` skill)

**Apply strongly when:**
- Business logic mixes with presentation or I/O
- A module handles both orchestration and implementation details
- Testing requires setting up UI or database to test logic

**Relax when:**
- Scripts or one-off tools where layering adds no value
- Performance-critical paths where cross-layer optimization is measurably necessary
- Prototype/MVP phase where domain boundaries are still unknown

**Tradeoff note:** "Mixing [concern A] and [concern B] in [module] because [justification — performance measurement, temporary MVP, etc.]."

---

### 5. High Cohesion, Low Coupling

**Core idea:** Modules are internally tight and externally minimal. Cohesion: elements within a module belong together. Coupling: minimize dependencies between modules.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Designing public APIs or shared libraries
- Building long-lived, maintained modules
- Multiple developers own different modules

**Relax when:**
- Internal implementation details that won't be reused
- Coupling is stable (both modules change together anyway)
- Decoupling introduces more complexity than it removes

**Tradeoff note:** "High coupling between [module_a] and [module_b] accepted because [reason — co-evolving, internal detail, etc.]."

---

### 6. Information Hiding

**Core idea:** Expose only what callers must know. Keep internals private.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Designing public APIs
- Module boundaries between teams or subsystems
- Implementation details likely to change

**Relax when:**
- Internal utility modules within a single cohesive subsystem
- Debug/inspection APIs that intentionally expose state
- Data classes that are pure value holders with no behavior

**Tradeoff note:** "Exposing [detail] in [interface] because [reason — performance, debugging necessity, etc.]."

---

### 7. Law of Demeter

**Core idea:** Only talk to your immediate friends. Avoid long call chains (`a.b.c().d()`).

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Call chains cross module boundaries
- Navigation through object graphs creates fragile dependencies
- The intermediate objects are implementation details

**Relax when:**
- Fluent/builder APIs designed for chaining
- Data structure traversal where each step is a stable domain concept
- Value objects with known, stable internal structure

**Tradeoff note:** "Using call chain [a.b.c().d()] because [reason — fluent API, stable structure, etc.]."

---

### 8. Composition Over Inheritance

**Core idea:** Prefer assembling behavior over subclassing.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Multiple independent dimensions of variation
- Deep inheritance hierarchies (3+ levels)
- Needing to combine behaviors from different "branches"

**Relax when:**
- Clear "is-a" taxonomic relationships (e.g., `Rectangle` is a `Shape`)
- Framework contracts requiring inheritance (e.g., Django models)
- Simple, stable hierarchies with one axis of variation

**Tradeoff note:** "Using inheritance for [class] because [reason — framework requirement, true is-a relationship, etc.]."

---

### 9. YAGNI — You Aren't Gonna Need It

**Core idea:** Don't build features or abstractions until needed.

**Enforcement:** Not enforced as a standalone rule. Related: `050-scope-autonomy.md` "No scope expansion" and AGENTS.md "Scope Creep — NEVER Do Things Outside the Spec."

**Apply strongly when:**
- Tempted to add "flexibility for future requirements"
- Designing abstractions with only one current implementation
- Adding configuration options no one has asked for

**Relax when:**
- Interface design where changing later is expensive (public APIs, database schemas)
- Well-understood requirements that are definitively coming next sprint
- Preventing lock-in to a vendor or technology (strategic abstraction)

**Tradeoff note:** "Building [feature/abstraction] now because [definitive upcoming need or strategic reason]."

---

### 10. Fail Fast

**Core idea:** Detect errors early. Don't let bad state propagate.

**Enforcement:** "Detect errors early. Don't let bad state propagate." (Also enforced in `200-errors-exception-handling.md` and `201-errors-missing-data.md`)

**Apply strongly when:**
- Validating inputs at module boundaries
- Assertions for invariants that must hold
- Pre-conditions for business-critical operations

**Relax when:**
- User-facing input where graceful error messages matter more than early detection
- Logging/metrics paths where failure shouldn't crash the system
- Recovery paths where retry is viable and preferred

**Tradeoff note:** "Using graceful handling instead of fail-fast for [input/path] because [reason — user experience, resilience requirement, etc.]."

---

### 11. Minimize Mutable State

**Core idea:** Prefer immutability. Reduce side effects.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Concurrent or parallel code where shared mutable state causes bugs
- Configuration that should be readonly after initialization
- Data transformations that compose cleanly as pure functions

**Relax when:**
- Performance-critical inner loops where object allocation is measurable overhead
- In-place algorithms on large datasets where copying is prohibitive
- State machines where mutation IS the domain model

**Tradeoff note:** "Using mutable state for [variable/structure] because [measurable performance reason or domain requirement]."

---

### 12. Idempotence

**Core idea:** Re-running operations should be safe. Critical for retries and distributed systems.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- API endpoints, message handlers, or any operation that may be retried
- Deployment scripts and CI/CD pipelines
- Database migrations and state transitions

**Relax when:**
- One-time operations with explicit "already done" checks in the caller
- Side-effect-only operations where idempotency engineering isn't worth it (e.g., sending a single notification)
- Interactive, user-driven operations where retries are meaningless

**Tradeoff note:** "Operation [name] is non-idempotent because [reason]. Caller must ensure at-most-once delivery."

---

### 13. Command–Query Separation

**Core idea:** A method either does something or returns something — never both.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Designing public APIs where callers need predictability
- Test interfaces where mocking return values must not cause side effects
- Functions that are used as both queries and commands create confusion

**Relax when:**
- Pop patterns (stack pop, queue dequeue) where returning the removed element is idiomatic
- Builder pattern methods that return `self` for chaining
- Stateful iterators where `next()` both advances and returns

**Tradeoff note:** "[method] both queries and mutates because [reason — pop pattern, builder chaining, etc.]."

---

### 14. Explicitness Over Implicitness

**Core idea:** No magic behavior. No hidden side effects.

**Enforcement:** Partially enforced. "No Magic Strings or Numbers: All literal strings and numbers that carry domain meaning must be extracted to named constants." (Also in `080-code-standards.md`)

**Apply strongly when:**
- Configuration and wiring that affects behavior at a distance
- Framework conventions that obscure what code actually does
- Implicit type coercion, global state, or "clever" metaprogramming

**Relax when:**
- Well-understood language idioms that are conventional, not surprising (e.g., list comprehensions, `with` statements)
- Framework conventions that reduce boilerplate without hiding logic (e.g., `__init__` imports)
- Obvious defaults that match the 90% case and are documented

**Tradeoff note:** "Using implicit [behavior/convention] because [reason — established idiom, framework convention, documented default]."

---

### 15. Observability First

**Core idea:** Logging, metrics, tracing, health checks. Designed in, not bolted on.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Production services and APIs
- Background jobs and async workers
- Distributed systems where failure modes are complex

**Relax when:**
- One-off scripts or local utilities
- Prototype/MVP phase where logging structure is still unknown
- Pure data transformations with clear input/output (function is its own documentation)

**Tradeoff note:** "Minimal observability for [component] because [reason — throwaway script, prototype, etc.]."

---

### 16. Defensive Programming

**Core idea:** Validate inputs. Handle impossible states explicitly. Never trust external data.

**Enforcement:** "Validate inputs. Handle impossible states explicitly. Never trust external data." (Also enforced in `090-data-integrity.md`)

**Apply strongly when:**
- Module boundaries (external input, API contracts)
- Security-sensitive paths (authentication, authorization, input parsing)
- Error paths that must never be silent (financial, medical, safety)

**Relax when:**
- Internal functions with trusted callers within the same module
- Performance-critical hot paths where validation overhead is measurable
- Pure functions with well-typed inputs where the type system provides defense

**Tradeoff note:** "Skipping defensive validation for [input/path] because [reason — trusted internal caller, type system guarantee, measured performance]."

---

### 17. Deterministic Behavior

**Core idea:** Same input → same output. Crucial for testing and reproducibility.

**Enforcement:** Not enforced — design guidance only.

**Apply strongly when:**
- Business logic, calculations, data transformations
- Test suites that must be reproducible
- APIs where callers expect consistent results

**Relax when:**
- Randomized algorithms (Monte Carlo, genetic algorithms) where nondeterminism is the point
- Cache invalidation or TTL-based logic where time is an explicit input
- Load shedding / circuit breaking where jitter prevents thundering herds

**Tradeoff note:** "Nondeterministic behavior in [component] because [reason — randomized algorithm, intentional jitter, etc.]. Seed set to [value] for reproducibility."

---

### 18. Small, Reversible Changes

**Core idea:** Keep PRs small. Keep commits atomic. Make rollback trivial.

**Enforcement:** Not enforced as a standalone rule. Related: git workflow (small commits, squash), AGENTS.md scope creep prohibition.

**Apply strongly when:**
- Multiple developers on the same codebase
- Production systems where rollback safety matters
- Complex features that can be decomposed into steps

**Relax when:**
- Mechanical bulk changes (renames, formatting) where atomicity is the unit
- Early prototyping where fine-grained commits add noise without value
- Tightly-coupled changes that cannot be meaningfully separated (e.g., schema + migration + code)

**Tradeoff note:** "Bundling [change_a] and [change_b] because [reason — tightly coupled, cannot deploy independently]."

---

### 19. Testability as a Design Constraint

**Core idea:** If it's hard to test, it's poorly designed. Prefer pure functions and isolated modules.

**Enforcement:** Partially enforced. "If a function exceeds 40 lines, decompose it." (Also in `080-code-standards.md` and `code-size-enforcement` skill)

**Apply strongly when:**
- Designing new modules or APIs
- Refactoring code that requires extensive mocking
- Writing business-critical logic with correctness requirements

**Relax when:**
- UI/presentation layer where visual testing is more appropriate than unit testing
- Integration with external systems where mock boundaries are inherently difficult
- Legacy adapters where testability redesign exceeds practical value

**Tradeoff note:** "Low testability in [module] because [reason — UI layer, external integration boundary, legacy adapter]."

---

### 20. Blast Radius Minimization

**Core idea:** Isolate failures. Isolate deployments. Isolate data ownership. Isolate scaling concerns.

**Enforcement:** "Isolate failures. Isolate deployments. Isolate data ownership. Isolate scaling concerns." (Also in `concern-separation-auditor` skill)

**Apply strongly when:**
- Designing system boundaries and service interfaces
- Managing shared state or data stores
- Deploying changes that affect multiple consumers

**Relax when:**
- Monolithic applications where isolation adds deployment complexity without benefit
- Internal utilities used by a single team
- Early-stage projects where boundaries are still forming

**Tradeoff note:** "Accepting wider blast radius for [change] because [reason — monolithic deployment, early stage, single team]."

---

## Quick Reference: Principles by Context

Not all 20 principles matter equally in every context. Use this table to prioritize:

| Context | Prioritize | Relax |
|---------|-----------|-------|
| One-off scripts | KISS, Fail Fast | SRP, SoC, Observability, Blast Radius |
| Public APIs | Info Hiding, SoC, Defensive Programming, CQS | Performance optimizations |
| Business logic | SRP, DRY, Determinism, Testability | Premature abstraction |
| Concurrency | Minimize Mutable State, Idempotence, Fail Fast | DRY (lock patterns may need duplication) |
| Data pipelines | Idempotence, Observability, Defensive Programming | CQS (side effects are inherent) |
| Prototypes/MVPs | KISS, YAGNI | SoC, Defensive Programming, Observability |

## Red Flags — When to Pause and Reconsider

| Thought | Check |
|---------|-------|
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

## Tradeoff Justification Format

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

## Cross-References

| Reference | Relationship |
|-----------|-------------|
| `080-code-standards.md` | Project-specific conventions (this skill owns principles, that guideline owns conventions) |
| `engineering-approach` skill | Workflow discipline — when to design, verify, communicate (this skill owns *what* principles to apply, that skill owns *when* in the process) |
| `code-size-enforcement` skill | Size limits — SRP and "No Monoliths" have hard limits there |
| `concern-separation-auditor` skill | Structural concern separation — this skill provides the design judgment perspective for SoC and Blast Radius |