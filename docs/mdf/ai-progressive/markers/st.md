---
marker: [st]
category: <Optional>
hierarchy_level: any
concerns: [data-handling]
cross_refs: []
tokens_estimate: 248
---


# \st status

*\key* \st

This is used to indicate how complete or thoroughly checked an entry is, e.g.:

*\fxv*

```text
 \st OK 
 \st no-print 
 \st check
```

Later you could filter the database to select only "check" records, export this filtered database
through MDF, and print the formatted output from Word. This makes it easy for a language
assistant to systematically check these entries.

If selected for output, the label "Status: " is usually added to this field and the
whole field is bracketed with "[ ]".

*\nt* This field does not normally print.

*\typ* <Optional>

## Data handling

Carries a status value tracking the entry's editorial state.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [Range_Sets](Range_Sets.md) Range Sets
