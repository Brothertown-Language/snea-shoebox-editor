---
marker: [hm]
category: <Reserved>
hierarchy_level: record
concerns: [structure, presentation]
cross_refs: [Character_Style_Codes]
tokens_estimate: 374
---


# \hm homonym number

*\key* \hm

This is field is used to differentiate homonym entries (lexemes that sound or are spelled the
same but have no semantic relationship). This field generally comes directly after the \lx field
and is simply followed by a 1, 2, or 3, etc.:

*\ftx*

```text
 \lx asw
 \hm 2
 \ps n
 ...
```

 (note the lack of punctuation in the \hm field) 

Any cross-reference to one of these entries should also include the homonym number, e.g.:

*\ftx*

```text
 \cf asw2
```

When the lexical database is converted to MS-Word format for printing, the homonym number
for both the entry and the cross-reference will be subscripted by MDF using the homonym
number character style.

For more on character styles, see:

\cf Character_Style_Codes

*\typ* <Reserved>

## Cross-references

- [Character_Style_Codes](Character_Style_Codes.md) Character Style Codes

## Structure

Homonym numbers differentiate same-form entries; the field belongs at the top of the record.

Listed under [Structure](../concerns/structure.md).

## Presentation

Prints the homonym number subscripted, using the homonym number character style.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [Range_Sets](Range_Sets.md) Range Sets
