---
marker: [pdl]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [Range_Sets, pdv, pde, pdn, pdr, pd]
tokens_estimate: 659
---


# \pdl paradigm label

*\key* \pdl

The paradigm field (\pd) field is used to define the general paradigm set a headword or
lexeme is associated with. But it is also useful to give the actual forms for a paradigm,
especially where a paradigm set is incomplete or irregular. For example, the third-singular
genitive marker normally possesses nouns with the form '-na', except with certain nouns,
where its form is irregular. Any noun that takes an irregular 3sGen form should be marked:

*\ftx*

```text
 \lx ow
 \ps n
 \ge jackfruit
 \gn nangka
 \pd n-fd
 \pdl 3sGEN
 \pdv owan
 \pde his/her jackfruit
 \pdn nangkanya
```

These paradigm label fields would typically print as:

*\fxv*

```text
 3sGEN: owan 'his/her jackfruit' 'nangkanya'.
```

(where the "3sGEN" is formatted as italic and the vernacular form and the glossing are
formatted with the appropriate language fonts)

*\nt* Note: The paradigm label (\pdl) fields can be used with or without the paradigm set (\pd) field.

*\fxv*

```text
You can use any label you need to mark a paradigm. Use Toolbox's Range Set 
feature to insure consistent labeling. For more information, see: 
```

\cf Range_Sets

*\nt* Note: All the fields in this bundle are made up of markers using three-letter codes.

The related fields to this set are:

\cf \pdv paradigm vernacular form

\cf \pde paradigm form-English gloss

\cf \pdn paradigm form-national gloss

\cf \pdr paradigm form-regional gloss

For more information on the paradigm fields, see:

\cf \pd paradigm set

*\typ* <Optional>

## Cross-references

- [Range_Sets](Range_Sets.md) Range Sets
- [pdv](pdv.md) pdv paradigm vernacular form
- [pde](pde.md) pde paradigm form (English gloss)
- [pdn](pdn.md) pdn paradigm form (national gloss)
- [pdr](pdr.md) pdr paradigm form (regional gloss)
- [pd](pd.md) pd paradigm set

## Semantics

Carries the label naming the paradigm.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [Old_and_Changed_Markers](Old_and_Changed_Markers.md) Old and Changed Markers
- [pd](pd.md) pd paradigm set
- [pde](pde.md) pde paradigm form (English gloss)
- [pdn](pdn.md) pdn paradigm form (national gloss)
- [pdr](pdr.md) pdr paradigm form (regional gloss)
- [pdv](pdv.md) pdv paradigm vernacular form
- [pl](pl.md) pl plural form
- [Range_Sets](Range_Sets.md) Range Sets
- [rd](rd.md) rd reduplication form(s)
- [sg](sg.md) sg singular form
