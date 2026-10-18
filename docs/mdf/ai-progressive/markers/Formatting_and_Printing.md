---
marker: [Formatting_and_Printing]
category: topic
hierarchy_level: topic
concerns: [presentation]
cross_refs: [References, Order_of_Fields, Summary_of_Fields]
tokens_estimate: 1024
---


# Formatting and Printing Your Dictionary and Finderlists

*\key* Formatting_and_Printing

So your lexicon is ready, and you want to print it. This assumes you've set up the
database to be an MDF type database . (An MDF type database not only uses the
MDF marker set but has checked the box in Database-Properties-Options labeled
"Multi-Dictionary Formatter"). 

### Specifying the Options

To print your lexicon, choose "Multi-Dictionary Formatter" from the File-Export
menu. Here you will be able to select the intended audience (either English or
national), the format (diglot, triglot, or a reversal finderlist), specify text for the
footer for each of these choices, select a filter (to limit the formatted document
to a smaller set of records), and specify whether you want Word opened
automatically (for Windows users). 

This dialog box also has an Options button which will allow you to set the basic
parameters the standard MDF print feature uses to create the formatted dictionary
or finderlists. These options include selecting specific fields to include or
exclude and some basic page formatting.

Clicking Export gives you a chance to specify a filename and location for the new
document. Clicking OK again starts the whole process. MDF goes through several
steps to format the document (detailed below). The final product is a Rich Text
Format (RTF) file.

### Open the RTF file in Word 

If you checked "Automatically open document in word processor", Toolbox
causes the word processor to automatically open the exported document;
otherwise you must open the RTF file yourself. 

### Finish the process of exporting from Toolbox 

To make the final formatting touches, choose the menu option "Finish exporting from Shoebox"
from under the Tools menu in Word. This runs the FinishExportingFromShoebox macro in the
document template. It updates style formatting and does a few other special formatting
operations. It also saves the exported file as a Word DOC file. 

*\nt*  Note: Word processor programs other than Microsoft Word may not be able to use 
the Word macro, and may even require a different template than is supplied with the
standard MDF printing process.

*\nt*  Note: Probably the most significant thing the Finish exporting from Shoebox macro
does is to load all the pictures.

If you need to change any style formatting, click on the text that needs changing,
choose Format, Style, and Modify. Make the changes needed, and remember to
check the "Add to Template" box before you choose OK so the style changes will
be available the next time you export.

### Print it 

If the document looks fine, choose File Print. 

*\nt* Note: Errors in the data should be corrected in Toolbox (and export again). If you correct errors 
in the Word document, they will still be there in the data when you export the next time.

_______________

*\nt* This concludes the general discussion of how to use MDF. 

For more information, see: 

\cf References

To return to the top of the database, simply close all unneeded windows, and then use the
Database-First Record menu option, or use the First Record button on the tool bar (or search
for 'aa').

To see the description of any particular field, simply right-click on its marker in
either of these lists (or anywhere else in this Help file):

\cf Order_of_Fields

\cf Summary_of_Fields

## Cross-references

- [References](References.md) References
- [Order_of_Fields](Order_of_Fields.md) Recommended Field Order
- [Summary_of_Fields](Summary_of_Fields.md) Summary of Fields (not ordered)

## Presentation

The central discussion of formatting the dictionary and finderlists for printing.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Printed_Field_Labels](Printed_Field_Labels.md) Printed Field Labels
- [Unknown_Fields](Unknown_Fields.md) Unknown Fields
