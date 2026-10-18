---
marker: [tb]
category: <Optional>
hierarchy_level: any
concerns: [presentation]
cross_refs: [lf, Punctuation_and_Special_Codes]
tokens_estimate: 651
---


# \tb table

*\key* \tb

This marks the following text as unformatted. Line-breaks and hard-coded tab characters will
be retained. (Multiple spaces are also be retained, but this is only useful if you define the
"Table" font in MS-Word to be a fixed width font.) 

A table, or list, of "cutting verbs" might look like this:

*\ftx*

```text
 \tb The summary of all types of cutting verbs:
 |{tab}fv:-akrina:|{tab}split in two lengthwise
 |{tab}fv:-boras:|{tab}cut s.t. in small pieces with a knife
 |{tab}fv:-dew:|{tab}chop s.t. into smaller pieces while standing it on end
 |{tab}fv:-het:|{tab}chop or hack with a machete
 |{tab}fv:-kety:|{tab}slice open and clean an animal
 |{tab}fv:-lary:|{tab}slice (like chilies, etc.)
 |{tab}fv:-lilit:|{tab}shave or carve
 |{tab}fv:-mair:|{tab}to adz wood
 |{tab}fv:-simat:|{tab}pop out or cut out coconut meat
```

In Toolbox, the table field is marked as a "No Word Wrap" field (in the Marker-Properties
dialog box). This allows you direct control over line-breaks and spacing. Note the |{tab}
bar-code in the above example. This tells Toolbox to insert a Tab at each of these places,
when the file is formatted by MDF or exported to an RTF file. (Currently Toolbox does not
support typing the Tab character directly.)

Inevitably, your tables will require some "tweaking" in MS-Word before you print the
dictionary. To do this, first convert the file to MS-Word format using MDF, and then search
for the "Table" style. After some tweaking, these could then be converted into a Word table
(with the Word menu command: Table-Convert Text to Table).

For a more powerful and in-depth approach to mapping the relations of lexical items, see:

\cf \lf lexical functions

For more on special codes supported by Toolbox, see:

\cf Punctuation_and_Special_Codes

*\nt* This is a "free-form" field. Punctuation and capitalization should be used as needed.

*\typ* <Optional>

## Cross-references

- [lf](lf.md) lf lexical function label
- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation

## Presentation

Marks a table (with caption) for the formatted output.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [cf](cf.md) cf confer/cross-reference
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [lf](lf.md) lf lexical function label
- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation
