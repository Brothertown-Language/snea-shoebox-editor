# Character Styles

From [Character Style Codes](../markers/Character_Style_Codes.md):

Character style codes can be used in any field (usually the information or discussion type
fields) to uniquely mark the specific language of the text that you are discussing. For example,
'fv:' marks the following word as vernacular text:

Character style codes are applied only to the following word. A space or any punctuation
(except the '-') terminates the style. The style codes must be in lower case, and there must not
be any space between the colon and the following word, e.g. 

Use the underline ( _ ) character to continue the style and link together words in a phrase, e.g.


MDF will format this whole phrase with the vernacular character style (the underlined
characters are converted to spaces). The question mark will not be included in the vernacular
style.

Character codes should be placed with the word, inside parentheses, quotes,
brackets, etc., otherwise the opening brackets will receive the character style
along with the word.

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

To explicitly control the character style or font of any phrase, word, or part of
word, use the underlying bar codes used by MDF. For example, to underline only
a part of a word, use the |u bar code:

The |u{} underlines the bracketed character ('a') only. Note that the curly braces
{} can contain any string of letters, numbers, spaces, or punctuation.

The complete list of explicit font codes follows:

Still supported, but not encouraged, are the older ("Manuscripter") style codes.

Underlining is more complex and so provides the following:

To format a homonym number in a discussion field you can use the explicit code:

For example:

To continue with the general discussion, jump to:

Full discussions:

- [Character Style Codes](../markers/Character_Style_Codes.md)
