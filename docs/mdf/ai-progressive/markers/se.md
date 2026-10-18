---
marker: [se]
category: <Reserved>
hierarchy_level: 3
concerns: [structure]
cross_refs: [Using_Subentries_or_Lexical_Entries, Sections_in_a_Lexical_Entry]
tokens_estimate: 500
---


# \se subentry (a polymorphemic form or a phrase)

*\key* \se

This is like the \lx field except it occurs within the record, marking the word (or phrase) as a
form derived from the root. Following this marker would be all the fields that comprise a
typical lexical entry. There can be several of these subentries within a record. Subentries can
also have multiple senses. A simple example using subentries would be:

*\ftx*

```text
 \lx bren
 \ps vi
 \ge play
 \ee Implies lack of focus or purpose.

 \se brenak
 \ps vt
 \ge play_s.t.
 \de play a game, or play with s.t.

 \se inabren
 \ps n
 \ge recreation ; entertainment

 \se rabrenak
 \ps n
 \ge toy
 \dt 17/Jun/92
```

This would typically print like the following:

*\fxv*

```text
bren vi. play. Implies lack of focus or purpose.
 brenak vt. play a game, or play with s.t.
 inabren n. recreation, entertainment.
 rabrenak n. toy.
```

But note that the subentries in this example are far too simplistic; they lack much of the
information that should be provided for these polymorphemic lexemes (definitions, example
sentences, cross-references, notes, etc.).

For a more detailed discussion of the issues involved in using subentries, see:

\cf Using_Subentries_or_Lexical_Entries

For information on the topic of sections in a lexical entry, see: 

\cf Sections_in_a_Lexical_Entry 

*\typ* <Reserved>

## Cross-references

- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry

## Structure

Section boundary: subentries add a further level of hierarchy within an entry.

Listed under [Structure](../concerns/structure.md).

## Backlinks

- [rd](rd.md) rd reduplication form(s)
