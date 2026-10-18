---
marker: [de]
category: <Basic>
hierarchy_level: any
concerns: [semantics]
cross_refs: [ge, dv, dn, dr, ue, oe, ee]
tokens_estimate: 601
---


# \de definition (English)

*\key* \de

This field is used to fully express the semantic domains of each sense of a lexeme in English.
For related information, see:

\cf \ge gloss (English)

### Hint 

If an entry has many English glosses, none of which are vitally important to differentiate while
glossing texts, give only one gloss in the \ge field (to simplify interlinearizing) and then give all
of the glosses in the \de and \re fields. When the dictionary is formatted, the \de field will be
used and the \ge field will be discarded. Also, because there are \re fields, the \ge field will be
ignored for reversing the database. 

For example, the Indonesian morpheme '-nya' means 'his' 'hers' or 'its', but for glossing '3sPOS'
may be adequate (if not preferable), but '3sPOS' is awkward for both a dictionary printout and
an entry in a reversed English finderlist. So, do something like this:

*\ftx*

```text
 \ge 3sPOS
 \re his ; hers ; its
 \de his, hers, its
```

This will simplify interlinearizing by keeping Toolbox from asking which gloss ('his', 'hers', or
'its') is appropriate for each occurrence of '-nya' in a text, and yet will allow your lexical
database to be more complete in its description of the meaning or semantic domain of the
lexeme.

Identical vernacular, national and regional fields are:

\cf \dv, \dn, and \dr

Closely related fields are:

\cf \ue, \oe, and \ee

*\typ* <Basic>

## Cross-references

- [ge](ge.md) ge gloss (English)
- [dv](dv.md) dv definition (vernacular)
- [dn](dn.md) dn definition (national)
- [dr](dr.md) dr definition (regional)
- [ue](ue.md) ue usage (English)
- [oe](oe.md) oe only [restrictions] (English)
- [ee](ee.md) ee encyclopedic information (English)

## Semantics

Carries the English definition — the primary meaning statement of an entry or sense.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [dn](dn.md) dn definition (national)
- [dr](dr.md) dr definition (regional)
- [dv](dv.md) dv definition (vernacular)
- [ee](ee.md) ee encyclopedic information (English)
- [ge](ge.md) ge gloss (English)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [oe](oe.md) oe only [restrictions] (English)
- [ue](ue.md) ue usage (English)
