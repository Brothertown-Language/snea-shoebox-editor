---
marker: [Free-form_Fields]
category: topic
hierarchy_level: topic
concerns: [presentation, data-handling]
cross_refs: [Range_Sets]
tokens_estimate: 642
---


# Free-form Fields

*\key* Free-form_Fields

In the standard MDF printing, the following fields are "free-form" fields, meaning
that MDF will not add periods, etc. to them; they are basically formatted as you
entered them. Therefore, when using these fields, you are encouraged to use
capitalization and proper punctuation. Free-form fields may be as long as you
need, e.g. several sentences.

*\ftx*

```text
 \rf reference * \pc picture
 \xv vernacular example \nt notes, general
 \xe English example \np notes on phonology
 \xn national example \ng notes on grammar
 \xr regional example \nd notes on discourse
 \ve variant form (English) \na notes on anthro.
 \vn variant form (National) \ns notes on socioling.
 \vr variant form (Regional) \nq questions
 \ur usage (regional)
 \or only (regional) 
 \er encyclopedic (Regional) 
 \tb table
```

The following fields are also free-form, except that the printing process will add
punctuation to the end if you do not. 

*\ftx*

```text
 \uv usage (vernacular) \ov only (vernacular)
 \ue usage (English) \oe only (English)
 \un usage (national) \on only (national)
```

 \ev encyclopedic (vern) 

 \ee encyclopedic (English) 

 \en encyclopedic (National) 

*\nt* If a field is not explicitly marked in its description as being a "free-form" field, then it is not one.

If a field is not a free-form field, you do not need to use any terminating punctuation; MDF
adds the needed punctuation to the end of each non-free-form field.

* The picture reference field is free-form so long as the field does not begin with .G. (which
marks it as a graphics link paragraph). See \pc for more information on the picture reference
field.

To continue on with the general discussion, jump to:

\cf Range_Sets

## Cross-references

- [Range_Sets](Range_Sets.md) Range Sets

## Presentation

Defines which fields accept free-form content in the formatted output.

Listed under [Presentation](../concerns/presentation.md).

## Data handling

Defines the terminating-punctuation conventions free-form field content must follow.

Listed under [Data handling](../concerns/data-handling.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
