---
marker: [mn]
category: <Optional>
hierarchy_level: any
concerns: [structure]
cross_refs: [va, Using_Subentries_or_Lexical_Entries]
tokens_estimate: 439
---


# \mn main entry form

*\key* \mn

This is used to reference a minimal entry back to its main entry. Minimal or "minor" entries
consist of abbreviated information, e.g.:

*\ftx*

```text
 \lx tado
 \ps adj
 \ge calm
 \mn teduh
```

This would typically print as:

*\fxv*

```text
 tado adj. calm; See main entry: teduh.
```

In this example, the minor entry "tado" has minimal information and contains a reference back
to the main semantically related entry "teduh". This cross-referencing is done through the \mn
field:

*\ftx*

```text
 \mn teduh
```

The main entry "teduh" would be more verbose, containing all of the information normally
included in a lexical entry. The "teduh" entry would also have the field "\va tado" to reference
the variant (dialect) form.

For related information, see:

\cf \va variant forms

For a detailed discussion of the issues involved in using minor (or minimal) entries, see:

\cf Using_Subentries_or_Lexical_Entries

*\typ* <Optional>

## Cross-references

- [va](va.md) va variant forms
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries

## Structure

Points a minimal entry at its main entry, keeping related lexemes connected without full records.

Listed under [Structure](../concerns/structure.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
- [va](va.md) va variant forms
