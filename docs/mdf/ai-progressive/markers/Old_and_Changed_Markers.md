---
marker: [Old_and_Changed_Markers]
category: topic
hierarchy_level: topic
concerns: [data-handling]
cross_refs: [lf, pd, pdl, The_MDF_Documentation]
tokens_estimate: 573
---


# Old and Changed Markers

*\key* Old_and_Changed_Markers

Within a couple years of the publication of the MDF manual in 1995, as the
number of users grew and became more widespread, there were recommendations
which modified the MDF marker set. These changes were reflected in the
modification to the MDF manual, "MDF-ch2 revised.doc".

In this database, some of the long-since un-recommended markers have been
removed from prominent display. (The MDF tables have not been changed.) In
addition, the database type distributed with the Toolbox Training Materials and the
Toolbox New Project Installer no longer includes these markers. These should all
be replaced by the paradigm markers.

 \1s \2s \3s \4s \1d \2d \3d \4d \1p \1i \1e \2p \3p \4p

For example, 

*\ftx*

```text
 \1s yoban
```

should be replaced by

*\ftx*

```text
 \pdl 1s
 \pdv yoban
```

In this example, the label which will be used in printing is placed in the \pdl
(paradigm label) field. The paradigm form itself is placed in the \pdv (paradigm
vernacular form) field. The paradigm approach has much greater flexibility, both
in the choice of labels and in allowing glosses in other languages.

In addition, the following are still included in the MDF database type file but
could be replaced by the paradigm approach.

 \sg Singular form \pl Plural form \rd Reduplication form

Similarly, these markers could use the lexical function approach.

 \an Antonym \sy Synonym

For examples and more details, see

\cf \lf the lexical function label

\cf \pd paradigm set

\cf \pdl the paradigm label

Be sure to also see

\cf The_MDF_Documentation

## Cross-references

- [lf](lf.md) lf lexical function label
- [pd](pd.md) pd paradigm set
- [pdl](pdl.md) pdl paradigm label
- [The_MDF_Documentation](The_MDF_Documentation.md) The MDF Documentation

## Data handling

Records marker changes across MDF versions for legacy data migration.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d](1s.md) Old verb paradigm markers
