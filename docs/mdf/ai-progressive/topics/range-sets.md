# Range Sets

From [Range Sets](../markers/Range_Sets.md):

Through the Range Set feature, Toolbox provides you with a powerful way to maintain
consistent labeling on any field where you are using a relatively small set of categorizing codes.
The most common fields for this are:

You are strongly encouraged to use Range Sets for these fields also:

Here are other fields which could benefit from the Range Set feature:

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

MDF standard printing provides a way (for certain fields) to list English and
National Audience substitutes for each label in the Range Sets. (The purpose of
the English substitute allows users to consistently change the formatted output
labels from the labels they use in their database, e.g. one-letter codes in the
paradigm label fields could be changed to more readable abbreviations).

These Range Set label substitutions are handled by the same CC tables that change the default
MDF field labels. For more information on these CC tables, see:

The areas in these CC tables that need "tweaking" are the special "group" sections, e.g.
group(gPartOfSpeech), group(gParadigmLabel), etc. Be sure to follow the instructions given in
these groups carefully. It is best to include a CC rule for every label in the field's Range Set.
To make sure you don't miss any:

To continue with the general discussion, jump to:

Full discussions:

- [Range Sets](../markers/Range_Sets.md)
