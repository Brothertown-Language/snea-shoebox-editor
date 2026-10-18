---
marker: [Range_Sets]
category: topic
hierarchy_level: topic
concerns: [presentation, data-handling]
cross_refs: [ps, pn, pd, sd, is, th, lf, pdl, hm, sn, bw, es, so, st, Printed_Field_Labels, Character_Style_Codes]
tokens_estimate: 1329
---


# Range Sets

*\key* Range_Sets

Through the Range Set feature, Toolbox provides you with a powerful way to maintain
consistent labeling on any field where you are using a relatively small set of categorizing codes.
The most common fields for this are:

\cf \ps part of speech

\cf \pn part of speech (national)

\cf \pd paradigm set

\cf \sd semantic domain

\cf \is index of semantics

\cf \th thesaurus

You are strongly encouraged to use Range Sets for these fields also:

\cf \lf lexical function

\cf \pdl paradigm form label 

Here are other fields which could benefit from the Range Set feature:

\cf \hm homonym number

\cf \sn sense number

\cf \bw borrowed word (source of a loan word)

\cf \es etymology source

\cf \so source of data/information

\cf \st status of the lexical entry

The easiest way to start a Range Set for a particular field, is to Right-Click on the
field marker (option-click on the Macintosh) and select the "Range Set" tab from
the Marker Properties dialog box that pops up. You can enter the labels directly
(separated by a <space>) or use the Build Range Set feature. This will build a
Range Set on the current field marker using the contents of all occurrences of
this field in all of the currently opened databases of this type. This is a great way
to start a new Range Set on an existing database or to compile a new list at any
time of what is currently in use (to see how consistent you are being, e.g. am I
using : or _ to concatenate complex labels, did I add a new label when I already
had one that is spelled almost the same, etc.).

*\nt* Do not build a Range Set on a field which does not have a closed set of possible contents. 

### Changing Range Set Labels (for the \ps, \lf, and \pdl fields)

MDF standard printing provides a way (for certain fields) to list English and
National Audience substitutes for each label in the Range Sets. (The purpose of
the English substitute allows users to consistently change the formatted output
labels from the labels they use in their database, e.g. one-letter codes in the
paradigm label fields could be changed to more readable abbreviations).

*\nt* This ability to make Range Set label substitutions is limited to the \ps, \lf, and \pdl fields. (If
more fields need to be covered, contact Toolbox@sil.org.

*\fxv*

```text
Note: with this feature, you no longer need to use the \pn field to output national
parts of speech. (But if you ever want to sort or browse on the national part of speech, 
you will still need to use \pn.)
```

These Range Set label substitutions are handled by the same CC tables that change the default
MDF field labels. For more information on these CC tables, see:

\cf Printed_Field_Labels

The areas in these CC tables that need "tweaking" are the special "group" sections, e.g.
group(gPartOfSpeech), group(gParadigmLabel), etc. Be sure to follow the instructions given in
these groups carefully. It is best to include a CC rule for every label in the field's Range Set.
To make sure you don't miss any:

*\ftx*

```text
 1. In Toolbox, Right-click on the field marker, to go to its 
 properties sheet.
 2. Click on the "Range Sets..." button
 3. Click on "Build Range Set"
 4. Use the mouse to select all of the Range Set labels in the 
 edit window on the left.
 5. Copy them to the Clipboard (<Ctrl-C>)
 6. Open Notepad (or any text editor) and Paste in the labels
 (that is <Ctrl-V>).
 7. Now you can print the labels or save them to a file.
 8. Use Notepad (or whatever) to edit the appropriate CC table
 and add a CC rule for each label in your Range Set.
```

*\nt* For more information on Range Sets, see the Shoebox helps file.

To continue with the general discussion, jump to:

\cf Character_Style_Codes

## Cross-references

- [ps](ps.md) ps part of speech
- [pn](pn.md) pn part of speech (national)
- [pd](pd.md) pd paradigm set
- [sd](sd.md) sd semantic domain
- [is](is.md) is index  of  semantics
- [th](th.md) th thesaurus
- [lf](lf.md) lf lexical function label
- [pdl](pdl.md) pdl paradigm label
- [hm](hm.md) hm homonym number
- [sn](sn.md) sn sense number
- [bw](bw.md) bw borrowed word
- [es](es.md) es etymology-source
- [so](so.md) so source of data
- [st](st.md) st status
- [Printed_Field_Labels](Printed_Field_Labels.md) Printed Field Labels
- [Character_Style_Codes](Character_Style_Codes.md) Character Style Codes

## Presentation

Covers the Range Set label substitutions applied when coded fields print.

Listed under [Presentation](../concerns/presentation.md).

## Data handling

Explains building and maintaining the controlled value lists (Range Sets) behind coded fields.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Free-form_Fields](Free-form_Fields.md) Free-form Fields
- [lf](lf.md) lf lexical function label
- [pd](pd.md) pd paradigm set
- [pdl](pdl.md) pdl paradigm label
- [pn](pn.md) pn part of speech (national)
- [Printed_Field_Labels](Printed_Field_Labels.md) Printed Field Labels
- [ps](ps.md) ps part of speech
