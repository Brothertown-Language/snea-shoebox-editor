---
marker: [pc]
category: <Optional>
hierarchy_level: any
concerns: [presentation]
cross_refs: []
tokens_estimate: 470
---


# \pc picture

*\key* \pc

This contains either the book and page number reference of a relevant picture
(you've either sketched in a notebook or found in a picture book), or a graphics
link for a PCX file of a picture you want to include in your printed dictionary.

If the field does not begin with '.G.' as in a graphics link, then the field is treated as "free-
form". The field is output near the end of an entry paragraph, and the print tables put
parentheses ( ) around the whole field (to set it off from other types of information).

If the \pc field begins with a graphics link mark (.G.), then it is NOT a "free-form" field and
should follow the basic form below:

*\ftx*

```text
 \pc .G.sago.pcx;1.5";1";PCX
```

The .G. marks this as a graphics link; next follows the filename of the picture; next is the width
(here 1.5") and then the height (1") and finally the graphics format (PCX). Each bit of
information is separated by a semicolon.

When the dictionary is formatted, the graphics information is moved to the beginning of the
entry, subentry, or sense in which the \pc field is found. This will cause the text to flow around
the picture. Sizes much larger than 1.5"x1.5" are not recommended. In double column format
the picture is placed flush right in the column; in single column format the picture is flush right
to the right margin.

*\nt* This is a "free-form" field, if it is not a Graphics Link paragraph. Punctuation and capitalization
should be used as needed.

*\typ* <Optional>

## Presentation

References a picture placed with the entry in the formatted output.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
