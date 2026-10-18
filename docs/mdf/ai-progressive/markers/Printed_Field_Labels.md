---
marker: [Printed_Field_Labels]
category: topic
hierarchy_level: topic
concerns: [presentation]
cross_refs: [Formatting_and_Printing, Range_Sets, Unknown_Fields]
tokens_estimate: 923
---


# Printed Field Labels

*\key* Printed_Field_Labels

MDF adds field labels to many of the fields as it formats your lexicon for
printing. These labels are explicitly noted in the discussion of each of the field
markers. MDF allows for these field labels to be changed for either English or
National audiences.

By default, MDF uses the following two CC tables to make the label substitutions:

*\ftx*

```text
 MDF_eng.cct (for English labels)
 MDF_inz.cct (for national (Indonesian)language labels)
```

MDF also comes with other label tables. For example, for French and Spanish:

*\ftx*

```text
 MDF_frn.cct (for French labels)
 MDF_spn.cct (for Spanish labels)
```

These CC tables are in the MDF folder, just under the Toolbox program folder. 

*\nt* For MDF to work properly, all of MDF's CC tables need to be copied to your Projects folder.
(This is the folder where you keep your project (PRJ) files, langauge (LNG) files, and database
type (TYP) files.)

Try one of these "canned" CC tables first, if these won't meet your needs, you can edit them so
that they put on the exact labels that you need.

*\nt* These files are specified in the File-Export-MDF-Options-Audience dialog box. 

To change a field label:

*\ftx*

```text
 1. IMPORTANT: First, using File Manager or Explorer, to copy the 
 CCT file you want to change to a new filename.
 2. Next open the new CCT file in Notepad.
 3. At the end of this file you will find a section marked as 
 "group(gLabel)"; under here are all of the field labels that
 MDF adds to the beginning of fields. The following are a few
 of the label-changing lines from one of these files:
```

"Ant:" > "Lawan:" c \an Antonym

"Read:" > "Baca:" c \bb Bibliography

"From:" > "Pinjaman:" c \bw Borrowed word (loan)

*\ftx*

```text
 4. Carefully change each label in the "Lawan:" column that needs
 changing. Be careful you do NOT delete the " marks! 
 5. Save the file to the new name (be careful that Notepad doesn't
 stick on a .TXT extension on the file --if it does, rename it).
 6. Now go back to Toolbox and the MDF Export-Options-Audience box 
 to give the name of the new CC table you created.
```

In these CC tables there is also options for making consistent changes to your lexical function
(\lf) labels, part of speech (\ps) labels, and paradigm form (\pdl) labels. This allows you to keep
your Range Sets labels for these all in one language, but when the dictionary is printed for
another audience, the labels are changed appropriately.

For a detailed description of the MDF formatting process, see:

\cf Formatting_and_Printing

For related information on how MDF can also substitute Range Set labels, see:

\cf Range_Sets

To continue with the general discussion, jump to:

\cf Unknown_Fields

## Cross-references

- [Formatting_and_Printing](Formatting_and_Printing.md) Formatting and Printing Your Dictionary and Finderlists
- [Range_Sets](Range_Sets.md) Range Sets
- [Unknown_Fields](Unknown_Fields.md) Unknown Fields

## Presentation

Documents the field labels the formatted output prints before field content.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [on](on.md) on only [restrictions] (national)
- [ov](ov.md) ov only   [restrictions]   (vernacular)
- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation
- [Range_Sets](Range_Sets.md) Range Sets
- [un](un.md) un usage (national)
- [uv](uv.md) uv usage (vernacular)
