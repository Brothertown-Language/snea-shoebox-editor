---
marker: [ee]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [en, er, de, ue, oe, Character_Style_Codes]
tokens_estimate: 943
---


# \ee encyclopedic information (English)

*\key* \ee

A field researcher has an incredible opportunity to assimilate intuitive knowledge of the
language and culture of the people with whom he/she works. This type of information is
invaluable to others who have no access to the language area (or at least no extended contact
with the language community).

This knowledge is often never codified. Now Toolbox provides a simple means by which a
researcher can "put on paper" this kind of information. Once added, the lexical database
becomes more than a "dictionary" but a "knowledge-base" of the language.

This field crosses over with the \de, \ue, and \oe fields, but is intended for more verbose
explanations of the lexeme (headword, subentry or sense). Basically, the researcher should use
this field to encode any additional information needed by a non-native speaker to understand
and use this lexeme properly. For example, the lexeme "hatw" (in Selaru) can be described
with the following fields:

*\ftx*

```text
 \de a fired, earthen, baking form used for making fv:skyerker
 \ee Often today this is replaced by a cast iron griddle, much 
 like a waffle iron, which is frequently found in the shape 
 of four hearts.
```

MDF does not add any label to this field, but simply formats it as entered. 

### Tip

Since MDF does not format or add any label to this field, you can actually use this field to
include additional information about a lexical entry which is not handled by any of the other
fields that MDF supports. You can even add your own label to this information. It's not pretty,
but it works. For example, if you wanted to create a new field to keep track of the weather (a
hypothetical example to be sure), you could enter your observations thus:

*\ftx*

```text
 \ee |fl{Weather: }The sun is hot with scattered showers expected.
```

The special character code " |fl{ }" tells MDF that the data contained in the curly braces needs
to be formatted as a label. The rest of the field is treated just like a normal encyclopedic field.

*\nt* Note: Using the encyclopedic fields in this manner should not be a common practice, as this will
make it impossible for Shoebox or any other program to know exactly what kind of data is
contained in your encyclopedic fields. But in a pinch, it does allow for this kind of flexibility.

Identical national and regional language fields are:

\cf \en and \er

Related fields include:

\cf \de, \ue, and \oe 

For more on special character formatting codes, see:

\cf Character_Style_Codes

*\nt* This is a "free-form" field. Punctuation and capitalization should be used as needed.

*\typ* <Optional>

## Cross-references

- [en](en.md) en encyclopedic information (national)
- [er](er.md) er encyclopedic information (regional)
- [de](de.md) de definition (English)
- [ue](ue.md) ue usage (English)
- [oe](oe.md) oe only [restrictions] (English)
- [Character_Style_Codes](Character_Style_Codes.md) Character Style Codes

## Semantics

Carries encyclopedic information that extends the definition with cultural or world knowledge.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [de](de.md) de definition (English)
- [en](en.md) en encyclopedic information (national)
- [er](er.md) er encyclopedic information (regional)
- [ev](ev.md) ev encyclopedic information (vernacular)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [na](na.md) na notes  on   anthropology
- [ns](ns.md) ns notes on sociolinguistics
- [oe](oe.md) oe only [restrictions] (English)
- [ue](ue.md) ue usage (English)
