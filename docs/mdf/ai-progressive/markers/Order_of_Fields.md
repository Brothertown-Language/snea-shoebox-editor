---
marker: [Order_of_Fields]
category: topic
hierarchy_level: topic
concerns: [structure, presentation]
cross_refs: [Alternate_Hierarchy, Sections_in_a_Lexical_Entry, Summary_of_Fields]
tokens_estimate: 1685
---


# Recommended Field Order

*\key* Order_of_Fields

The following are all of the fields in their recommended order for a lexical entry. The order
shown here assumes you are using the standard hierarchy (the alternate hierarchy only varies
in the hierarchical order of the \sn, \se, and \ps fields). For more information on the alternate
hierarchy, see:

\cf Alternate_Hierarchy

The field order shown here is nearly identical to the order in which MDF outputs
the fields when formatting your lexicon. This needs to be stressed that when MDF
formats your lexicon, the fields are rearranged to (nearly) the following order.
This is to provide a consistent field sequence to each and every lexical entry (a
much desired goal of any published work).

The main differences between the recommended order given here and the order in which
MDF outputs the fields are as follows: 

 1) the \lx and \lc fields -- in the database, the \lx field must come first, 

 but for printing, the citation (\lc) field is the first field out (if it exists). 

 2) the gloss and definition fields -- the gloss field prints only if there

 is no definition field. 

 3) the reverse fields and the word gloss fields -- these generally do not 

 print; but if you request them, they print grouped together after the 

 definitions.

It is recommended that you use the database template feature of Toolbox to help you maintain
a consistent ordering of your fields.

*\nt* Deviating from this order (especially for the \se, \ps, \pn, and \sn fields) could foul MDF
formatting, since these fields also serve to mark section boundaries. For more on this, see:

\cf Sections_in_a_Lexical_Entry

In the following list, the following codes are used:

*\ftx*

```text
 'B' marks 'Basic' fields (17 total)
 'R' marks 'Reserved' fields (4 total)
 (all other fields are 'Optional')

---------------------------------------------------------
 \lx (lexical entry) ONLY ONE PER LEXICAL ENTRY
R \hm (homonym number)
R \lc (lexical citation)
 \ph (phonetic/phonemic form)

R \se (subentry)
B \ps (part of speech)
B \pn (part of speech-national)
R \sn (sense number)

 \gv (gloss-vernacular)
 \dv (definition-vernacular)
B \ge (gloss-English)
B \re (reversal form-English) [default set not to print]
 \we (word gloss-English) [default set not to print]
B \de (definition-English)
B \gn (gloss-national)
B \rn (reversal form-national) [default set not to print]
 \wn (word gloss-national) [default set not to print]
B \dn (definition-national)
 \gr (gloss-regional)
 \rr (reversal form-regional) [default set not to print]
 \wr (word gloss-regional) [default set not to print]
 \dr (definition-regional) 

 \lt (literal meaning)
 \sc (scientific name) 

B \rf (reference to notebooks, etc.)
B \xv (example-vernacular)
B \xe (example-English)
B \xn (example-national)
 \xr (example-regional)

 \uv (usage-vernacular)
 \ue (usage-English)
 \un (usage-national)
 \ur (usage-regional)
 \ev (encyclopedic info.-vernacular)
 \ee (encyclopedic info.-English)
 \en (encyclopedic info.-national)
 \er (encyclopedic info.-regional)
 \ov (only [restrictions]-vernacular)
 \oe (only [restrictions]-English)
 \on (only [restrictions]-national)
 \or (only [restrictions]-regional)

 \lf (lexical function label)
 \lv (vernacular lexeme referenced by the lexical function)
 \le (lexical function-English gloss of referenced lexeme)
 \ln (lexical function-national gloss of referenced lexeme)
 \lr (lexical function-regional gloss of referenced lexeme)
 \sy (synonyms)
 \an (antonyms)
 \mr (morphemic representation)
B \cf (confer/cross-reference)
B \ce (cross-reference-English gloss)
B \cn (cross-reference-national gloss)
 \cr (cross-reference-regional gloss)
 \mn (main entry form)
 \va (variant forms, e.g. dialect, etc.)
 \ve (variant forms comment-English)
 \vn (variant forms comment-national)
 \vr (variant forms comment-regional)
 \bw (borrowed word)
 \et (etymology)
 \eg (etymology-gloss)
 \es (etymology-source) [default set not to print]
 \ec (etymology-comment) [default set not to print]

 \pd (paradigm set)
 \pdl (paradigm label)
 \pdv (paradigm vernacular form)
 \pde (paradigm form-English gloss)
 \pdn (paradigm form-national gloss)
 \pdr (paradigm form-regional gloss)
 \sg (singular noun form)
 \pl (plural noun form)
 \rd (reduplication forms)
 \1s (1st person singular verb form)
 \2s (2nd person singular verb form)
 \3s (3rd person singular verb form)
 \4s (singular non-human/non-animate verb form)
 \1d (1st person dual verb form)
 \2d (2nd person dual verb form)
 \3d (3rd person dual verb form)
 \4d (dual non-human/non-animate verb form)
 \1p (1st person plural-generic verb form)
 \1e (1st person plural-exclusive verb form)
 \1i (1st person plural-inclusive verb form)
 \2p (2nd person plural verb form)
 \3p (3rd person plural verb form)
 \4p (plural non-human/non-animate verb form)

 \tb (table)

 \sd (semantic domain) [default set not to print]
 \is (index of semantics) [default set not to print]
 \th (thesaurus) [default set not to print]

 \bb (bibliographic reference)
 \pc (picture reference)

B \nt (notes, etc.)
 \np (notes on phonology)
 \ng (notes on grammar)
 \nd (notes on discourse)
 \na (notes on anthropology)
 \ns (notes on sociolinguistics)
 \nq (questions)

 \so (source of data) [default set not to print]
 \st (status) [default set not to print]
B \dt (datestamp) [default set not to print]
--------------------end of example record--------------------
```

*\nt*  (To see the description of any particular field, simply right-click on its marker.)

To continue this discussion, jump to:

\cf Summary_of_Fields

## Cross-references

- [Alternate_Hierarchy](Alternate_Hierarchy.md) A Sense-Oriented Hierarchy
- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry
- [Summary_of_Fields](Summary_of_Fields.md) Summary of Fields (not ordered)

## Structure

Lists every field in its recommended order for a lexical entry, the backbone of entry structure.

Listed under [Structure](../concerns/structure.md).

## Presentation

Shows the order in which MDF outputs fields when formatting the lexicon.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Alternate_Hierarchy](Alternate_Hierarchy.md) A Sense-Oriented Hierarchy
- [Formatting_and_Printing](Formatting_and_Printing.md) Formatting and Printing Your Dictionary and Finderlists
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
