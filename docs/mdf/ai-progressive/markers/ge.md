---
marker: [ge]
category: <Basic>
hierarchy_level: any
concerns: [semantics]
cross_refs: [de, re]
tokens_estimate: 544
---


# \ge gloss (English)

*\key* \ge

This is intended for interlinear morpheme-level glossing. It is used for reversing the dictionary
if an \re field is not present (or is present but empty). It is also used as an English definition in
the printed dictionary if there is no \de field (or it is present but empty).

The user may enter data either with each gloss getting its own field:

*\ftx*

```text
 \ge put_out
 \ge move
```

The underline character '_' in the example glosses above is to force Toolbox to
treat the multiple word gloss 'put out' as a single gloss. When printing a
dictionary, the underlines normally will be converted to spaces. 

Similarly, a dot ("period" or "full stop") can be placed between the words instead
of the underline:

*\ftx*

```text
 \ge put.out
 \ge move
```

An oldere style allows you to list the glosses strung together, separated by a
semicolon with a space on either side of it (so as to be unlike any normal
punctuation):

*\ftx*

```text
 \ge put_out ; move
```

Toolbox can recognize either format and when interlinearizing will give the user
the choice of both glosses in either case. The sequence ' ; ' is also converted to ', '
by MDF printing when formatting a dictionary or finderlist.

The advantage of keeping your glosses in separate fields is that if you setup
Toolbox to sort on the \ge fields (to get a type of finderlist), it will sort on all of
the glosses; but if the glosses are all concatenated, Toolbox will only sort on the
first form.

For important related information, see:

\cf \de definition (English)

\cf \re reverse form (English)

*\typ* <Basic>

## Cross-references

- [de](de.md) de definition (English)
- [re](re.md) re reversal form (English)

## Semantics

Carries the English gloss used for interlinear text and quick meaning equivalence.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [de](de.md) de definition (English)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [re](re.md) re reversal form (English)
