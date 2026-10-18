---
marker: [Introduction]
category: topic
hierarchy_level: topic
concerns: [structure, data-handling]
cross_refs: [The_MDF_Documentation, When_MDF_Fails_to_Meet_Your_Requirements, lx, hm, lc, ph, ps, pn, sn, va, ve, vn, vr, mr, lt, sc, sd, is, th, pd, pdl, pde, pdn, pdr, pdv, cf, mn, lf, le, ln, lr, lv, bw, et, eg, es, ec, de, dn, dr, dv, ee, en, er, ev, ue, un, ur, uv, oe, on, or, ov, ge, gn, gr, gv, re, rn, rr, we, wn, wr, rf, xe, xn, xr, xv, pc, tb, bb, nt, so, st, dt, Order_of_Fields]
tokens_estimate: 2693
---


# Standard Lexical Database Field Markers (for MDF)

*\key* Introduction

### Introduction

MDF is a set of markers designed for multi-lingual dictionaries. It was created by
Grimes and Coward and documented in, "Making Dictionaries". MDF is also a
printing (export) process. Because this printing process was built into the
Windows version of Shoebox (now Toolbox), both have spread -- each feeding the
popularity of the other. The MDF marker set is now used by linguists worldwide.
For further information on the MDF manual itself, see

\cf The_MDF_Documentation

This file is designed to be an MDF help file available in Toolbox while you work
on your lexicon. Most of the information in this file describes the standardized
MDF field markers and their contents (i.e. what kind of information the markers
mark). 

To look up the description of a field marker, use the Toolbox Search command
and type the field marker code, (without the backslash \ character), e.g. for
information on the \ps field, search for 'ps' (no quotes). 

Another way to look up a marker is to click the Browse button and scroll down
the list of markers until you see what you're interested in. 

Browse is also one way

to see the titles of information available on other topics. Remember, too, that the

"aa" record contains a full list of other topics available.

MDF is not perfect and does not fit everyone's needs. If you need fields that aren't
available, or if the printout is not what you want, read the following:

\cf When_MDF_Fails_to_Meet_Your_Requirements

### Organizing the Markers

One problem faced by users of MDF is that of "too many markers". The following
summary is an attempt to make the number seem less threatening.

#### ... by Language

A large number of markers come in sets of three or four. MDF attemps to
generalize the need for multiple languages by recognizing four possible
languages and providing markers for them. Most of the MDF markers are two
characters long. The second character is often (not always) a language character.

 _e indicates English language markers

 _n indicates National language markers

 _r indicates Regional language markers

 _v indicates Vernacular language markers

Some markers have the language assumed. So the lexeme (lx) and subentries (se)
are always vernacular language, even though they don't end with "v" (and even
though subentry ends with "e"). Some of these, like the variant (va), have related
markers (comments in this case) for the other three languages.

#### ... by Function

In a real sense, everything in the entry relates to the headword. But some fields
are more tightly related than others. Some are more related to the definition,
some are your personal notes on different topics, etc. This is an attempt to
organize the approximately 100 MDF markers.

*\nt* Note: The following does not give the order in which these fields normally 
appear in a dictionary.

*\nt* Note: A marker like de* means that there is a set of language markers 
beginning with d: dv, dn, dr, de. A right click on such a marker will take 
you to the one, and the others will be listed there.

##### Information Relating Directly to the Headword

\cf lx lexeme hm homonym number lc lexical citation form

\cf ph phonetic (pronunciation) ps part of speech pn National part of speech

\cf sn sense number

##### Information about the Headword

\cf va variant form (also ve* comments) mr morphology lt literally

\cf sc scientific name sd semantic domain is index of semantics th thesaurus

\cf pd paradigm class pdl paradigm label (also pdv* paradigm form & glosses)

##### Other forms of the Headword

\cf va variant form (also ve* comments) mr morphology 

\cf pd paradigm class pdl paradigm label (also pdv* paradigm form & glosses)

##### Related entries

\cf cf cross reference mn main-entry cross reference

\cf lf lexical function (like synonym, causal, generic, deverbal noun, locative, etc.)
 (also lv* lexical function form and glosses)

##### Origins

\cf bw borrowed word et etymology (also eg gloss, es source, ec comment)

##### Definition and Range of Meaning

\cf de* definition ee* encyclopedic information (expanded definition)

\cf ue* usage oe* "only" (restrictions)

\cf ge* gloss (for interlinear) re* reversal (for finder lists) we* word-level gloss

##### Examples

\cf rf source of example (reference) xv* examples and translations

\cf pc picture snd sound vid video

##### Dialects

*\nt* There are no specifically "dialect" markers. Various alternative approaches can be used.
The revision of Chapter 2 discusses the following as possibilities.

\cf va* (variant) ue* (usage) oe* (only / restrictions)

\cf lf SynD (lexical function: synonym dialect)

##### Miscellany

\cf tb table (caption) bb bibliography nt notes (various kinds)

\cf so source of data st status dt date last edited

If you are unsure which marker to use, first look under 'Summary_of_Fields' for
the code you want, and then search for that field marker.

### Three Types of Field Markers

In this database, each field marker is describe by of the following categories:

*\typ* <Basic> 

This marks all of the "basic" field markers. These are the field markers which will
be useful to the most people. Consider including all of the basic field markers in
your Toolbox lexical database template, so they will be inserted automatically
into each of your new records. Leaving a basic field empty is okay.

*\typ* <Reserved>

This marks the "reserved" fields, meaning, these fields serve a crucial function in
the MDF formatting process and so should be used only if needed. These are the
 \lc, \hm, \se, and \sn fields. Empty reserved fields should not be included in your
records, i.e. if present, they should contain data.

*\typ* <Optional>

This marks the "optional" fields. These are the more technical fields given to
cover just about every topic. You may want to include some of these in your
database template as well. And no doubt, some of these optional fields will be of
no use to you. Like with basic fields, leaving an optional field empty is okay.

### Multiple Fields

The number of occurrences of any given field is not restricted. But in printing
through the standard MDF export process, multiple occurrences of a given field
will be concatenated within a hierarchical section, e.g. with a sense, or if there is
no sense, then within a part of speech section, or subentry section, etc. Multiple
occurrences within the same record but in separate sections (sense, part of
speech, or subentry) are kept separate.

To continue this discussion, jump to:

\cf Order_of_Fields

## Cross-references

- [The_MDF_Documentation](The_MDF_Documentation.md) The MDF Documentation
- [When_MDF_Fails_to_Meet_Your_Requirements](When_MDF_Fails_to_Meet_Your_Requirements.md) When MDF Fails to Meet Your Requirements
- [lx](lx.md) lx lexeme or headword of the lexical entry
- [hm](hm.md) hm homonym number
- [lc](lc.md) lc lexical citation
- [ph](ph.md) ph phonetic/phonemic form
- [ps](ps.md) ps part of speech
- [pn](pn.md) pn part of speech (national)
- [sn](sn.md) sn sense number
- [va](va.md) va variant forms
- [ve](ve.md) ve variant comment (English)
- [vn](vn.md) vn variant comment (national)
- [vr](vr.md) vr variant comment (regional)
- [mr](mr.md) mr morphemic representation
- [lt](lt.md) lt literal meaning
- [sc](sc.md) sc scientific name
- [sd](sd.md) sd semantic domain
- [is](is.md) is index  of  semantics
- [th](th.md) th thesaurus
- [pd](pd.md) pd paradigm set
- [pdl](pdl.md) pdl paradigm label
- [pde](pde.md) pde paradigm form (English gloss)
- [pdn](pdn.md) pdn paradigm form (national gloss)
- [pdr](pdr.md) pdr paradigm form (regional gloss)
- [pdv](pdv.md) pdv paradigm vernacular form
- [cf](cf.md) cf confer/cross-reference
- [mn](mn.md) mn main entry form
- [lf](lf.md) lf lexical function label
- [le](le.md) le lexical function (English gloss)
- [ln](ln.md) ln lexical function (national gloss)
- [lr](lr.md) lr lexical function (regional gloss)
- [lv](lv.md) lv vernacular lexeme referenced by the lexical function
- [bw](bw.md) bw borrowed word
- [et](et.md) et etymology
- [eg](eg.md) eg etymology-gloss
- [es](es.md) es etymology-source
- [ec](ec.md) ec etymology-comment
- [de](de.md) de definition (English)
- [dn](dn.md) dn definition (national)
- [dr](dr.md) dr definition (regional)
- [dv](dv.md) dv definition (vernacular)
- [ee](ee.md) ee encyclopedic information (English)
- [en](en.md) en encyclopedic information (national)
- [er](er.md) er encyclopedic information (regional)
- [ev](ev.md) ev encyclopedic information (vernacular)
- [ue](ue.md) ue usage (English)
- [un](un.md) un usage (national)
- [ur](ur.md) ur usage (regional)
- [uv](uv.md) uv usage (vernacular)
- [oe](oe.md) oe only [restrictions] (English)
- [on](on.md) on only [restrictions] (national)
- [or](or.md) or only [restrictions] (regional)
- [ov](ov.md) ov only   [restrictions]   (vernacular)
- [ge](ge.md) ge gloss (English)
- [gn](gn.md) gn gloss (national)
- [gr](gr.md) gr gloss (regional)
- [gv](gv.md) gv gloss (vernacular)
- [re](re.md) re reversal form (English)
- [rn](rn.md) rn reversal form (national)
- [rr](rr.md) rr reversal form (regional)
- [we](we.md) we word-level gloss (English)
- [wn](wn.md) wn word-level gloss (national)
- [wr](wr.md) wr word-level gloss (regional)
- [rf](rf.md) rf reference to notebooks, texts, etc.
- [xe](xe.md) xe translation of example (English)
- [xn](xn.md) xn translation of example (national)
- [xr](xr.md) xr translation of example (regional)
- [xv](xv.md) xv example sentence (vernacular)
- [pc](pc.md) pc picture
- [tb](tb.md) tb table
- [bb](bb.md) bb bibliographic reference
- [nt](nt.md) nt notes, etc.
- [so](so.md) so source of data
- [st](st.md) st status
- [dt](dt.md) dt datestamp
- [Order_of_Fields](Order_of_Fields.md) Recommended Field Order

## Structure

Organizes the marker set by language and function and defines the field-type categories.

Listed under [Structure](../concerns/structure.md).

## Data handling

Explains the field-type categories (<Basic>, <Reserved>, <Optional>) and template guidance.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
