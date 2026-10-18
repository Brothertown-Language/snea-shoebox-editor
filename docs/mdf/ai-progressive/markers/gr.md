---
marker: [gr]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [dr, rr]
tokens_estimate: 446
---


# \gr gloss (regional)

*\key* \gr

This helps clarify the national language gloss in the prominent regional language of the area.
This is also used as a regional definition in the printed dictionary if there is no \dr field present
(or it is present but empty).

The user may enter data either with each gloss getting its own field:

*\ftx*

```text
 \gr kasi_pinda
 \gr kasi_pulang
```

Or with the glosses strung together, separated by a semicolon with a space on either side of it
(so as to be unlike any normal punctuation):

*\ftx*

```text
 \ge kasi_pinda ; kasi_pulang
```

Toolbox can recognize either format and when interlinearizing will give the user the choice of
both glosses in either case.

The underline character '_' in the example glosses above is to force Toolbox to treat the
multiple word gloss 'kasi pinda' as a single gloss. MDF will convert underline characters in
gloss fields to spaces automatically. The sequence ' ; ' is also converted to ', ' by MDF when
formatting a dictionary or finderlist.

If this field is included in the output, MDF adds a label and brackets "[ ]" around it and it is
treated as part of the national field.

For important related information, see:

\cf \dr definition (regional)

\cf \rr reversal form (regional)

*\typ* <Optional>

## Cross-references

- [dr](dr.md) dr definition (regional)
- [rr](rr.md) rr reversal form (regional)

## Semantics

Carries the regional-language gloss for interlinear use.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [dr](dr.md) dr definition (regional)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
