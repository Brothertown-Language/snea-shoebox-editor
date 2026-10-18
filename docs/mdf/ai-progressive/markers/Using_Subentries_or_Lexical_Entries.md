---
marker: [Using_Subentries_or_Lexical_Entries]
category: topic
hierarchy_level: topic
concerns: [structure]
cross_refs: [Sections_in_a_Lexical_Entry, Alternate_Hierarchy, mn, cf, lf, Free-form_Fields]
tokens_estimate: 1414
---


# Using Subentries, Lexical Entries, and Minimal Entries

*\key* Using_Subentries_or_Lexical_Entries

A common question that all lexicographers must face when wrestling with
complex (polymorphemic) lexemes is whether to incorporate them in the lexicon
as subentries under the lexical entry of their root lexeme, or to place them in the
lexicon as independent lexical entries. This is not an easy question to answer, but
it is addressed in greater detail in Chapter 4 (section 4.6) of the MDF field
manual (Coward and Grimes, 1995). For this database, we will summarize the two
options below:

### 1. Using Subentries and Minimal Entries

If you want to keep all related (root and polymorphemic) lexemes together, use the subentry
method shown below (this is a simplified example): 

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

This would print as:

*\fxv*

```text
bren vi. play. Implies lack of focus or purpose.
 brenak vt. play a game, or play with s.t.
 inabren n. recreation, entertainment.
 rabrenak n. toy.
```

This method allows you to see all of the related pieces close together. But you have to know
where to look. And this is a major problem; outsiders will not know that to find a discussion of
"inabren" they must look under "bren". To make this easier for new users, we recommend you
also make extensive use of "Minimal Entries" (essentially the same as "minor entries") -- these
are lexical entries that have only the most basic fields (maybe a \ps field and a gloss field), but
they include the \mn "main entry" field which provides the sign-post back to the lexical entry
where more information can be found.

The minimal entry for "inabren" might be:

*\ftx*

```text
 \lx inabren
 \ps n
 \ge recreation
 \mn bren
```

When printed the \mn field typically has the label "See main entry:". 

That is all there is to this minimal entry. For this reason, it is expected that the subentry for
"inabren" would look very much like a full lexical entry; it would contain verbose definitions,
have example sentences, multiple senses (if needed), cross-referencing, and any encyclopedic
information, notes, or comments that are needed to elucidate this lexeme, i.e. it would be as
though a full lexical entry were stuck right inside another lexical entry. (The above example of
subentry use obviously falls short of this expectation -- it is merely an example.)

But practically speaking, many find it difficult to actually put the same amount of effort into
embellishing a subentry as they would into a main lexical entry. For this reason, and for the fact
that such embellished records soon become enormous, you might find the alternative way
better for you:

### 2. Lexical Entries and Cross-referencing

The alternative is nearly the exact opposite: make all lexemes (roots or polymorphemic forms)
main lexical entries. But in order to see the relationships between the scattered pieces, you will
need to use an extensive cross-referencing system. MDF provides the \cf and the \lf field
bundles for this.

Again using the above example, the "bren" lexical entry would include the following fields:

*\ftx*

```text
 \cf brenak
 \ce play s.t.

 \cf inabren
 \ce recreation

 \cf rabrenak
 \ce toy
```

These \cf fields reference full lexical entries for both "inabren" and for "rabrenak". If you wish
to provide even further information regarding the relationship between the "bren" lexeme and
these referenced lexemes, use the \lf field (the \lf labels shown here are not certain):

*\ftx*

```text
 \lf Vgoal
 \lv brenak
 \le play s.t.

 \lf Ngoal
 \lv inabren
 \le recreation

 \lf Ninst
 \lv rabrenak
 \le toy
```

This strategy keeps the individual records smaller and still provides a way to see
what all the related forms are and their general meanings and relationships. But
for more detailed information about a related lexeme requires searching through
the lexicon (easy in Toolbox, but tedious when in book form).

You will need to decide which strategy will work best for you.

For more information on sections in a lexical entry, see:

\cf Sections_in_a_Lexical_Entry

\cf Alternate_Hierarchy

For information on related fields, see:

\cf \mn main entry form

\cf \cf general cross-reference

\cf \lf lexical function cross-reference

To continue with the general discussion, jump to:

\cf Free-form_Fields

## Cross-references

- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry
- [Alternate_Hierarchy](Alternate_Hierarchy.md) A Sense-Oriented Hierarchy
- [mn](mn.md) mn main entry form
- [cf](cf.md) cf confer/cross-reference
- [lf](lf.md) lf lexical function label
- [Free-form_Fields](Free-form_Fields.md) Free-form Fields

## Structure

Lays out the structural choice between subentries, lexical entries, and minimal entries.

Listed under [Structure](../concerns/structure.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Alternate_Hierarchy](Alternate_Hierarchy.md) A Sense-Oriented Hierarchy
- [mn](mn.md) mn main entry form
- [se](se.md) se subentry (a polymorphemic form or a phrase)
- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry
- [va](va.md) va variant forms
