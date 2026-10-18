---
marker: [lv]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [lf, le, ln, lr, cf]
tokens_estimate: 443
---


# \lv vernacular lexeme referenced by the lexical function

*\key* \lv

This field is used in MDF for encoding the vernacular lexeme in a lexical function network.
The \lv field "points to" the vernacular lexeme (morpheme, word, or phrase) that is semantically
related to the current headword as mapped or cataloged by the label in the \lf field. An
example of its use would be:

*\ftx*

```text
 \lx feten <-- the headword/lexeme
 \ps n
 \ge millet
 ...
 \lf Gen <-- the lexical function/relationship
 \lv agat <-- the related lexeme
 \le grain <-- the English gloss of 'agat'
 ...
```

In this example, 'agat' ('grain') is in a Generic relationship to 'feten' ('millet'). Note that the
lexeme 'agat' should also appear in the lexicon.

For more information, see:

\cf \lf lexical function label

Glossing fields for this vernacular lexeme are:

\cf \le, \ln, and \lr

For generic cross-referencing, see:

\cf \cf cross-reference

*\typ* <Optional>

## Cross-references

- [lf](lf.md) lf lexical function label
- [le](le.md) le lexical function (English gloss)
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
- [cf](cf.md) cf confer/cross-reference

## Semantics

Carries the vernacular lexeme referenced by the lexical function.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [le](le.md) le lexical function (English gloss)
- [lf](lf.md) lf lexical function label
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
