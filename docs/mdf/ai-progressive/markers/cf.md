---
marker: [cf]
category: <Basic>
hierarchy_level: any
concerns: [structure]
cross_refs: [lf, tb, ce, cn, cr]
tokens_estimate: 946
---


# \cf confer/cross-reference

*\key* \cf

This is a generic reference marker used to link together any two related entries in the lexicon.
For example, in Selaru, '-aswasw kaha' means 'high water mark' and needs to cross-reference
'manahma' (the entry for 'rising tide') and visa-versa.

The \cf field is bundled with the \ce, \cn, and \cr gloss fields, so this example would be encoded
as:

*\ftx*

```text
 \cf manahma
 \ce rising tide
 \cn air naik
 \cr
```

and would typically print in a triglot dictionary as:

*\fxv*

```text
 See: manahma 'rising tide' 'air naik'.
```

Multiple cross reference bundles are usually concatenated with semicolons ';' as
seen in:

*\ftx*

```text
 \cf manahma
 \ce rising tide
 \cn air naik
 \cr
 \cf mety2
 \ce low tide
 \cn
 \cr
 \cf rean
 \ce high tide
 \cn
 \cr
```

This would typically print in a diglot dictionary as:

*\fxv*

```text
 See: manahma 'rising tide'; mety2 'low tide'; 
 rean 'high tide'.
```

(Note that actually the vernacular text is usually be printed as bold, and the '2' for
the homonym number of 'mety' as subscripted, but these can't be displayed that
way in Toolbox.)

One major short coming of using the cross-reference fields (rather than the lexical function
fields) is that the semantic relationship between the two related lexemes is not made explicit.
But it is often the case that a researcher will know there is some kind of relationship between
two lexemes but is unclear as to the nature of that relationship. This is what the \cf field is
good for. And once the relationship is determined, the cross-reference information could then
be transferred to an \lf field bundle.

It is not uncommon for there to be many lexemes that are interrelated. This creates a myriad
of cross-references, where each lexeme of a given type is cross-referenced to all other
lexemes of that type. Adding new entries to the group can also be very tedious. A simple
solution to this is to choose one lexeme as the focal point and have all other related lexemes
refer only to that one. That focal lexeme will then contain a listing of all other lexemes in the
group, by using either a series of \lf (lexical function) bundles, to describe the relationships
between that focal lexeme and each of the other lexemes, or by using the \tb (table) field to
make an actual list of the other lexemes and their meanings. 

For more on grouping cross-references or mapping related lexemes, see:

\cf \lf lexical function label

\cf \tb table

For the English, national and regional glossing fields, see:

\cf \ce, \cn and \cr

*\typ* <Basic>

## Cross-references

- [lf](lf.md) lf lexical function label
- [tb](tb.md) tb table
- [ce](ce.md) ce cross-reference (English gloss)
- [cn](cn.md) cn cross-reference (national gloss)
- [cr](cr.md) cr cross-reference (regional gloss)

## Structure

The cross-reference field links entries to the entries and topics that discuss them.

Listed under [Structure](../concerns/structure.md).

## Backlinks

- [ce](ce.md) ce cross-reference (English gloss)
- [cn](cn.md) cn cross-reference (national gloss)
- [cr](cr.md) cr cross-reference (regional gloss)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [le](le.md) le lexical function (English gloss)
- [lf](lf.md) lf lexical function label
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
- [lv](lv.md) lv vernacular lexeme referenced by the lexical function
- [sy](sy.md) sy synonym
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
