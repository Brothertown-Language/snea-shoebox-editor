# Planning: Executive Summary Guidance

## Purpose

Executive summaries enable **linguists, anthropologists, and domain experts** to quickly evaluate specification relevance, scope, and implications without reading the full specification.

---

## What Executive Summaries Answer

A well-formed executive summary answers:

- **What** is being proposed?
- **Why** is it needed?
- **What domain knowledge** is assumed or affected?
- **What constraints** limit the solution?

The summary provides sufficient context for a domain expert to assess whether the specification touches their area of concern.

---

## Creating Executive Summaries

### Determine What the Reader Needs to Know

An executive summary should contain only information relevant to the specification. Ask:

1. What is the deliverable? (files, functions, data structures, behaviors)
2. Does this specification touch linguistic data or terminology?
3. Are there domain-specific concepts the reader should recognize?
4. What limits what can be done? (technical constraints, preservation requirements, compatibility)

If a question has no relevant answer, omit it entirely.

### Include Linguistic Concerns Only When Relevant

Specifications may touch zero or more of these concerns. Include only those directly affected:

| Concern | When Relevant |
|---------|---------------|
| **Text normalization** | String matching, comparison, search operations |
| **Orthographic systems** | Writing systems, transliteration, variant spellings |
| **Lexical semantics** | Term definitions, polysemy, glossaries |
| **Morphology** | Word forms, inflection, morpheme boundaries |
| **Phonology** | IPA, phonemic/phonetic representation, tone |
| **Interlinear glossing** | Leipzig Glossing Rules notation |
| **Language identification** | ISO 639 codes, naming conventions |
| **Data provenance** | Source attribution, speaker consent |
| **Corpus methodology** | Frequency, annotation, concordance |

A specification handling string comparison needs text normalization context. A specification reorganizing UI layout likely needs none. Include only what applies.

### State Constraints When They Matter

If the specification has hard boundaries the reader must know, state them concisely:

- **Preservation requirements** (e.g., "original orthography must be preserved")
- **Compatibility requirements** (e.g., "must support existing data format")
- **Technical restrictions** (e.g., "no external dependencies")

If no special constraints exist beyond normal development practices, omit this entirely.

### Assume Basic Knowledge

The reader has basic computer systems knowledge. Do not explain:
- What Unicode is
- What an API is
- What a database does

Do explain domain-specific terms that appear in the specification itself.

### Be Concise

Aim for the reader to grasp intent in under 30 seconds. If the summary exceeds 150 words, consider whether all details are necessary.

### Avoid Padding

Do not include:
- Hedging or qualification ("this important feature", "carefully designed")
- Marketing language ("robust", "comprehensive", "state-of-the-art")
- Repeating the problem statement multiple ways
- Implementation details that belong in the body
- Explanations of what the reader already knows

---

## Examples

### Example A: Text Processing Specification

> Add Unicode normalization utilities for lexical comparison. Affects text normalization—specifications handling string matching must document NFC/NFD decisions for diacritic handling. Constraint: preserve original orthography in storage; generate normalized search keys.

### Example B: UI Layout Specification

> Reorganize sidebar controls into collapsible sections to improve navigation for large datasets. No special domain constraints.

### Example C: Database Schema Specification

> Add language-enumeration table with ISO 639-3 codes. Requires language identification—use ISO 639-3 for all language references. Existing records without language codes remain valid; migration provides defaults.

### Example D: API Endpoint Specification

> Add REST endpoint for retrieving morphological analyses. No linguistic data handling—accepts pre-tokenized input, returns analysis objects.

---

## Descriptive vs. Rigid

This guidance is **descriptive**, not prescriptive. Agents have flexibility to:

- Omit sections that don't apply
- Include relevant context beyond the suggested categories
- Adjust length based on specification complexity

Do NOT impose mandatory structure. The goal is clarity for domain experts, not checkbox compliance.

---

*Source: Created per [SPEC] Executive Summary Guidance for Spec Documents (#34)*