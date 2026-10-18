---
marker: [pd]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [Range_Sets, pdl, pdv, pde, pdn, pdr]
tokens_estimate: 594
---


# \pd paradigm set

*\key* \pd

This is used for specifying the noun or verb class, gender, or other paradigm set that the
lexeme or headword is associated with. These classes are generally given labels or numbers to
differentiate them. It is assumed that the classes are explained elsewhere (like the introduction
to the dictionary) and all that is needed here is the class label or number, e.g.: 

*\ftx*

```text
 \pd 3 
```

Mnemonic codes are actually better than numbers (since what the number represents is very
difficult to remember), e.g.:

*\ftx*

```text
 \pd met:vrt
```

might refer to a "verb root which metathesizes with its subject prefix". This is much easier to
decode than "3". For consistency be sure to use Toolbox's Range Set feature on this field. For
more information, see: 

\cf Range_Sets

This would typically print as: 

*\fxv*

```text
 Prdm: met:vrt.
```

To give the actual vernacular form for a paradigm (especially needed where the
paradigm is incomplete or is irregular in form), MDF provides the following
fields:

\cf \pdl paradigm label

\cf \pdv paradigm vernacular form

\cf \pde paradigm form-English gloss

\cf \pdn paradigm form-national gloss

\cf \pdr paradigm form-regional gloss

*\typ* <Optional>

## Cross-references

- [Range_Sets](Range_Sets.md) Range Sets
- [pdl](pdl.md) pdl paradigm label
- [pdv](pdv.md) pdv paradigm vernacular form
- [pde](pde.md) pde paradigm form (English gloss)
- [pdn](pdn.md) pdn paradigm form (national gloss)
- [pdr](pdr.md) pdr paradigm form (regional gloss)

## Semantics

Carries the paradigm set identifying an inflectional class.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [Old_and_Changed_Markers](Old_and_Changed_Markers.md) Old and Changed Markers
- [pde](pde.md) pde paradigm form (English gloss)
- [pdl](pdl.md) pdl paradigm label
- [pdn](pdn.md) pdn paradigm form (national gloss)
- [pdr](pdr.md) pdr paradigm form (regional gloss)
- [pdv](pdv.md) pdv paradigm vernacular form
- [pl](pl.md) pl plural form
- [Range_Sets](Range_Sets.md) Range Sets
- [rd](rd.md) rd reduplication form(s)
- [sg](sg.md) sg singular form
