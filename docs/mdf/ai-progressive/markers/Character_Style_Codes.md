---
marker: [Character_Style_Codes]
category: topic
hierarchy_level: topic
concerns: [presentation]
cross_refs: [Punctuation_and_Special_Codes]
tokens_estimate: 1329
---


# Character Style Codes

*\key* Character_Style_Codes

Character style codes can be used in any field (usually the information or discussion type
fields) to uniquely mark the specific language of the text that you are discussing. For example,
'fv:' marks the following word as vernacular text:

*\ftx*

```text
 \ue This usage is a bit blunt. Most people don't say 
 this directly, rather they refer to where they are 
 going, e.g. fv:keta to refer to 'outside the village',
 but fv:-dai is used in familiar settings.
```

Character style codes are applied only to the following word. A space or any punctuation
(except the '-') terminates the style. The style codes must be in lower case, and there must not
be any space between the colon and the following word, e.g. 

*\ftx*

```text
 fv:sabun is okay
 fv: sabun won't work (the fv: is treated as normal text)
```

Use the underline ( _ ) character to continue the style and link together words in a phrase, e.g.

*\ftx*

```text
 \ue In the phrase fv:Mala_sai_desy_de? there is a sense of 
 anger or rudeness.
```


MDF will format this whole phrase with the vernacular character style (the underlined
characters are converted to spaces). The question mark will not be included in the vernacular
style.

Character codes should be placed with the word, inside parentheses, quotes,
brackets, etc., otherwise the opening brackets will receive the character style
along with the word.

### Basic Language and Character Codes

*\ftx*

```text
 fv: (font--vernacular)
 fe: (font--English)
 fn: (font--national language)
 fr: (font--regional language)

 fs: (font--standard)
 fb: (font--bold)
 fi: (font--italic)

 uc: (underline character)
 ub: (underline--bold)
 ui: (underline--italic)
```

### Other Character Codes

*\ftx*

```text
 sc: (underline a scientific name--not 
 required in the \sc field)
```

The uc: code is able to detect which type of field it is used in. If the field is a
vernacular field uc: will underline with bold characters (following the vernacular
character style); if the field uses the national language, uc: will underline italic
characters; and if the field uses English, uc: will underline normal characters (to
follow the character style for English). If you want to specifically control the
underlining character style, use ui: and ub:.

If you need to tweak your formatted dictionary or reversed finderlists and apply a character
style where you had forgotten to place a code, simply use the same character style that
MS-Word uses to format other such text (e.g. the vernacular font in MS-Word uses the
"f_vernacular" style). Just be sure to also add the missing character style code in your lexical
database too, otherwise you'll have to "tweak" the output every time.

### Explicit Font Codes

To explicitly control the character style or font of any phrase, word, or part of
word, use the underlying bar codes used by MDF. For example, to underline only
a part of a word, use the |u bar code:

*\ftx*

```text
 \xv Aulopo|u{a} au lae weidu.
```

The |u{} underlines the bracketed character ('a') only. Note that the curly braces
{} can contain any string of letters, numbers, spaces, or punctuation.

The complete list of explicit font codes follows:

*\ftx*

```text
 |fv{ } Vernacular font
 |fe{ } English font
 |fn{ } National font
 |fr{ } Regional font
 |fs{ } Standard font (for general punctuation)
 |fl{ } The font for field labels

 |fb{ } Bold font 
 |fi{ } Italic font
```

Still supported, but not encouraged, are the older ("Manuscripter") style codes.

Underlining is more complex and so provides the following:

*\ftx*

```text
 |u{ } General underlined character font (as shown above) 
 |uc{ } Specific regular underlined character font 
 |ub{ } Specific underlined, bold font 
 |ui{ } Specific underlined, italic font
```

To format a homonym number in a discussion field you can use the explicit code:

*\ftx*

```text
 |hm{ } Homonym number font 
```

For example:

*\ftx*

```text
 \ec This lexeme is now a homonym with fv:asw|hm{1} 'dog' 
 because proto *l ~ s in Selaru resulting in a loss 
 of contrast.
```

*\nt* If you choose to use these explicit style codes, you must not forget the closing brace ' } '. If you
do, the rest of the field will be considered a part of the specified font!

*\nt* Actually, any field marker can become a character style code and transmit its formatting 
to the data enclosed in the curly brackets. This is mostly useful for the fields mentioned
already (sc, hm) but any field code can be used.

To continue with the general discussion, jump to:

\cf Punctuation_and_Special_Codes

## Cross-references

- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation

## Presentation

Documents the character styles MDF applies to printed output components.

Listed under [Presentation](../concerns/presentation.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [ee](ee.md) ee encyclopedic information (English)
- [hm](hm.md) hm homonym number
- [Punctuation_and_Special_Codes](Punctuation_and_Special_Codes.md) Punctuation
- [Range_Sets](Range_Sets.md) Range Sets
