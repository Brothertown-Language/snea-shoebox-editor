---
marker: [gn]
category: <Basic>
hierarchy_level: any
concerns: [semantics]
cross_refs: [dn, rn]
tokens_estimate: 401
---


# \gn gloss (national)

*\key* \gn

This is intended for interlinear morpheme-level glossing. It is used for reversing the dictionary
if an \rn field is not present (or is present but empty). It is also used as a national language
definition in the printed dictionary if there is no \dn field (or it is present but empty).

The user may enter data either with each gloss getting its own field:

*\ftx*

```text
 \gn keluarkan
 \gn pindahkan
```

Or with the glosses strung together, separated by a semicolon with a space on either side of it
(so as to be unlike any normal punctuation):

*\ftx*

```text
 \gn keluarkan ; pindahkan
```

Toolbox can recognize either format and when interlinearizing will give the user the choice of
both glosses in either case.

MDF will convert the ' ; ' sequence to ', ' when formatting the dictionary. (MDF will also
automatically convert any underline character '_' in a gloss field to a space when formatting.)

For important related information, see:

\cf \dn definition (national)

\cf \rn reversal form (national)

*\typ* <Basic>

## Cross-references

- [dn](dn.md) dn definition (national)
- [rn](rn.md) rn reversal form (national)

## Semantics

Carries the national-language gloss for interlinear use.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [dn](dn.md) dn definition (national)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [rn](rn.md) rn reversal form (national)
