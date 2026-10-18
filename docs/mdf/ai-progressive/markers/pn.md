---
marker: [pn]
category: <Basic>
hierarchy_level: 1
concerns: [structure, semantics]
cross_refs: [ps, Range_Sets]
tokens_estimate: 400
---


# \pn part of speech (national)

*\key* \pn

This field is used to classify the part of speech with labels found in national language
dictionaries. Consistent labeling is important. Use Toolbox's Range Set feature for this field.

MDF requires that the \pn field follow the \ps field:

*\ftx*

```text
 \ps n (noun)
 \pn kb (the national abbreviate for 'noun')
```

*\nt* If the order is reversed, MDF will not function properly.

MDF will format the \pn field only if you specify that the output is for a national audience.
When a national audience is specified, the \pn field will replace the \ps field. But if there is no
 \pn field or it is empty, the \ps field will be output for the national audience as for an English
audience. 

For more information, see:

\cf \ps part of speech

For important information on Range Sets and on MDF's label substitution feature, see:

\cf Range_Sets

*\typ* <Basic>

## Cross-references

- [ps](ps.md) ps part of speech
- [Range_Sets](Range_Sets.md) Range Sets

## Structure

Section boundary: the national-language part of speech organizes sections directly within an entry.

Listed under [Structure](../concerns/structure.md).

## Semantics

Carries the national-language part of speech.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [ps](ps.md) ps part of speech
- [Range_Sets](Range_Sets.md) Range Sets
