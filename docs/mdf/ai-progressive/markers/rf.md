---
marker: [rf]
category: <Basic>
hierarchy_level: any
concerns: [data-handling]
cross_refs: [xv]
tokens_estimate: 470
---


# \rf reference to notebooks, texts, etc.

*\key* \rf

This field keeps the notebook reference for the following example sentence. This will enable
you to validate the example at a later date (e.g., if it comes from an early notebook, it may be
suspect).

The \rf, \xv, \xn, and \xe fields are considered "bundled" (or grouped) together. If you include
multiple examples for a single entry, subentry, or sense, be sure to include the fields grouped
together. 

*\ftx*

```text
 \rf nbk1.23.12
 \xv example1
 \xn ...
 \xe ...

 \rf nbk1.54.09
 \xv example2
 \xn ...
 \xe ... etc.
```

Usually these are grouped with the \rf field at the beginning of each bundle, but if you don't
want to use the \rf field, then the \xv field will mark the beginning of example sentence
bundles.

You may use as many different example sentence bundles as you need for each sense, part of
speech, and/or subentry in a record. Within a given section (e.g. sense), multiple examples are
printed one after the other. 

MDF adds the label "Ref: " to this field.

See also:

\cf \xv example sentence (vernacular)

*\nt* This is a "free-form" field. Punctuation and capitalization should be used as needed.

*\typ* <Basic>

## Cross-references

- [xv](xv.md) xv example sentence (vernacular)

## Data handling

Carries the reference to the notebook or text from which an example was taken.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [sn](sn.md) sn sense number
- [xe](xe.md) xe translation of example (English)
- [xn](xn.md) xn translation of example (national)
- [xr](xr.md) xr translation of example (regional)
- [xv](xv.md) xv example sentence (vernacular)
