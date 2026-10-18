---
marker: [When_MDF_Fails_to_Meet_Your_Requirements]
category: topic
hierarchy_level: topic
concerns: [presentation, data-handling]
cross_refs: []
tokens_estimate: 1192
---


# When MDF Fails to Meet Your Requirements

*\key* When_MDF_Fails_to_Meet_Your_Requirements

This topic is still under construction. Terse notes on common problems and
answers are below. Contact Toolbox@sil.org for more details or other problems.

### Typical problems

appearance of the printout -- modify the template in Word, check "add to
template" to keep changes for the next export; check Page Setup under Options
for columns, margins, odd-even -- these are not included in the template

labels in the wrong language -- check the set of files mdf_xxx.cct to see if the
language you want is available. if not, modify the mdf_eng.cct and save as an
appropriate name, then select that file by Modifying the Audience options.

labels in the wrong script -- modify the template in Word, check "add to template"
to keep changes for the next export

label needed after the field, not preceding -- contact Toolbox@sil.org. A more
flexible system is coming

punctuation is not what is wanted -- punctuation is very difficult to modify.
Contact Toolbox@sil.org. A more flexible system is coming.

some fields not included in the printout -- check list of markers to exclude; check
Options settings for various "include..." options; check Audience selection; check
diglot / triglot selection; check Finderlist selection

sorted order of the printout -- check language encoding assignment of \lx and \lc
in MDF.typ and also in MDF_RTF.typ, which MDF printing uses for final sorting.
(Do Project, Database types in order to check MDF_RTF.typ.)

fields are printed in the wrong order -- MDF standard printing reorders all fields
according to a specific pattern; a version which doesn't reorder is available.
contact Toolbox@sil.org for help on this. (Soon to be made widely available.)

marker NOT to be printed, not available -- no problem, create a new marker and
use it for whatever notes or questions you are wanting it for. Also, read the NOTE
ON ADDING MARKERS at the end.

marker to be printed but NOT FINAL printing, not available -- create the new
marker, check "include non-MDF field" under options and be sure it is in the list
of fields included (Select Fields to be Excluded button in Options). Note, such
fields will be printed at the end of the entry. Also, read the NOTE ON ADDING
MARKERS at the end.

marker for final printing not available -- be sure you understand what *is*
available (read the descriptions of the markers). MDF standard printing puts all
non-MDF fields at the end. If that's OK, be sure it's included for printing ("Select
Fields to be Excluded" button in Options). Also, read the NOTE ON ADDING
MARKERS at the end.

need markers for more scripts than are available, multiple scripts for the same
field (eg, lexeme) -- if it's only the lexeme (perhaps entered in Roman but you
want to print in script) AND you are not using the lexical citation option (\lc
field), then the \lc field can be used for the script form of the lexeme. Similarly,
if you don't have a regional language, you can use the various regional markers to
provide another script (Actually, you may have to shuffle the meanings of the
various "languages" in order to get the order you want.) -- these tricks are not
really encouraged, but can be made to work. If these don't meet your needs,
contact Toolbox@sil.org; a more flexible system is being developed. Also, read
the NOTE ON ADDING MARKERS at the end. 

*\nt* NOTE ON ADDING MARKERS: 

The MDF marker set is a standard recognized by various organizations. Additional
markers should not be added without good motivation. On the other hand, it is
also recognized that the marker set does not cover all possible reasonable needs.
If you are going to publish electronically or if you are going to archive your
dictionary through some organization, be sure they understand and approve the
marker set you are using. Also, include your database type file with the archive
and be sure your new markers have a good description. If you have legacy data, be
sure that the archiving or publishing organization has the appropriate font(s) and 
language encoding file(s).

## Presentation

Collects fixes for printout problems: appearance, labels, punctuation, and field order.

Listed under [Presentation](../concerns/presentation.md).

## Data handling

Collects fixes involving CC tables, encoding assignments, and marker availability.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
