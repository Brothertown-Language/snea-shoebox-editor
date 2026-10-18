---
marker: [Unknown_Fields]
category: topic
hierarchy_level: topic
concerns: [data-handling]
cross_refs: [Formatting_and_Printing]
tokens_estimate: 424
---


# Unknown Fields

*\key* Unknown_Fields

Any field marker in a lexical database that is not recognized by MDF is considered an
unknown or Non-MDF Field. 

*\nt* Normally MDF discards unknown fields from the formatted output. 

While it is always best to use available fields where possible (for the sake of functionality and
compatibility), if you should need to create a field not covered by the 102 MDF fields (say, for
some special bookkeeping or analysis chore), you may do so without worry. As a general rule,
any field marker of three or four letters is a non-MDF field. The only exceptions to this rule
are the new paradigm fields: \pdl, \pdv, \pde, \pdn, and \pdr.

*\nt* If you want MDF to include non-MDF fields in the formatted output, simply check "Include
non-MDF fields" under Options in the MDF Export dialog box.

All unknown fields are collected together and placed at the end of the section they occur in.
They are bracketed with [ ] and marked with the label: ??. 

To continue with the general discussion, jump to:

\cf Formatting_and_Printing

## Cross-references

- [Formatting_and_Printing](Formatting_and_Printing.md) Formatting and Printing Your Dictionary and Finderlists

## Data handling

Defines how unrecognized markers are handled in the database and the formatted output.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Printed_Field_Labels](Printed_Field_Labels.md) Printed Field Labels
- [xg](xg.md) xg (discontinued field)
