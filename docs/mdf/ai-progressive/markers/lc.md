---
marker: [lc]
category: <Reserved>
hierarchy_level: record
concerns: [structure, presentation]
cross_refs: []
tokens_estimate: 422
---


# \lc lexical citation

*\key* \lc

This should be added only if the lexical entry form is inappropriate for the printed dictionary,
and you want to substitute another form for the printed entry, e.g. you might want the entry
"lewat" printed as "léwat" if its stress pattern were not predictable.

Roots are commonly used as the lexeme form in Toolbox lexical databases, but if the language
affixes prepositionally, a dictionary printed with root forms as the entry form can be very
confusing to native speakers. In this case, you could choose a consistent conjugated form (e.g.
3s-verb form) for a citation form.

MDF will always replace the \lx field with the \lc field, if present, and then resort the dictionary
according to these fields. (You can choose to restrict MDF to sort the database only by the \lx
field, even for those entries with an \lc field. This restriction will not effect the \lc field though,
an \lc field will still print as the entry form for its record. Choosing to restrict MDF to the \lx
field may cause some citation forms to appear out of sequence.)

*\typ* <Reserved>

## Structure

Substitutes the printed headword form; the field belongs at the top of the record.

Listed under [Structure](../concerns/structure.md).

## Presentation

Supplies the form the printed dictionary shows as the headword.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [lx](lx.md) lx lexeme or headword of the lexical entry
