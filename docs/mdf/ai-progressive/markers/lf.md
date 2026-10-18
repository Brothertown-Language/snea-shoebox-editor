---
marker: [lf]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [lf, lv, le, ln, lr, Range_Sets, tb, cf, References]
tokens_estimate: 1091
---


# \lf lexical function label

*\key* \lf

For encoding the semantic networks of a language. The \lf field bundle includes the following
fields:

\cf \lf the lexical function or relationship label

\cf \lv vernacular lexeme referenced by that lexical function/relation

\cf \le English gloss of the vernacular lexeme

\cf \ln national gloss of the vernacular lexeme

\cf \lr regional gloss of the vernacular lexeme

MDF supports two ways of using the \lf bundles. A typical example using the
original (mixed data) method would be: 

*\ftx*

```text
 \lf Syn
 \lv -dew
 \le chop on end
 \ln
 \lr
```

(Note that empty fields are okay.) 

This lexical function would be typically print as:

*\fxv*

```text
 Syn: -dew 'chop on end'.
```

If the other glosses were filled in, they would be included in the printout (if a triglot dictionary
was requested). Multiple lexical function bundles are concatenated with a semicolon '; ', e.g.:

*\fxv*

```text
 Syn: -dew 'chop on end'; Syn: -sin 'split'.
```

Note: In the original MDF manual and even in the revision of Chapter 2 you will
see examples in which the label and the vernacular word were both in the \lf field.
For example, \lf Syn = -dew. This approach is now strongly discouraged. The user
is strongly encouraged to use the \lv field as shown in the examples in this record.

The recommended MDF method for handling lexical functions (using the \lv
field) has some distinct advantages over the old way: 

 1) Since the lexical function label sits by itself in the \lf field, you can use the
Toolbox Range Set feature to maintain consistent labeling. 

 2) Using \lf and \lv fields with the sort and jump features of Toolbox is much
easier. 

 3) Browsing on a database sorted by the \lv and \lf fields and displaying the \lv, 
 \lf, and \le fields will give a virtual \lv reversal view of your data -- allowing you
to see all of the lexical functions that any given lexeme has been categorized
under.

 4) New Toolbox features like integrity checks, range-set building, and word lists
will not work properly on the \lf field if it contains mixed data. 

 5) If the vernacular language is written in a non-Roman script, the lexeme and
lexical function label need to be in different fields since they have different
language encodings.

See also:

\cf \lv vernacular lexeme referenced by the lexical function label

For more information on Range Sets, see: 

\cf Range_Sets

For an alternative way to create a table of related lexical items, see: 

\cf \tb table

For generic cross-referencing, see:

\cf \cf confer/cross-reference

For more detailed information on language analysis through lexical functions, see the MDF field
manual (Coward and Grimes, 1995) and the article "Mapping a culture through networks of
meaning" (Grimes 1987). For referential information on these, see:

\cf References

*\typ* <Optional>

## Cross-references

- [lf](lf.md) lf lexical function label
- [lv](lv.md) lv vernacular lexeme referenced by the lexical function
- [le](le.md) le lexical function (English gloss)
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
- [Range_Sets](Range_Sets.md) Range Sets
- [tb](tb.md) tb table
- [cf](cf.md) cf confer/cross-reference
- [References](References.md) References

## Semantics

Carries the lexical function label relating an entry to other lexemes by sense relations.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [an](an.md) an antonym
- [cf](cf.md) cf confer/cross-reference
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [le](le.md) le lexical function (English gloss)
- [lf](lf.md) lf lexical function label
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
- [lv](lv.md) lv vernacular lexeme referenced by the lexical function
- [Old_and_Changed_Markers](Old_and_Changed_Markers.md) Old and Changed Markers
- [Range_Sets](Range_Sets.md) Range Sets
- [sy](sy.md) sy synonym
- [tb](tb.md) tb table
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
