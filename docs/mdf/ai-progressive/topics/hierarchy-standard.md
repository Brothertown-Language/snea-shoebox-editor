# The Standard Hierarchy

From [Sections in a Lexical Entry](../markers/Sections_in_a_Lexical_Entry.md):

MDF has two built-in hierarchical structures that should be flexible enough to
meet most needs. (See "Alternate_Hierarchy" for a discussion of MDF's other
hierarchy.) The field codes that mark the boundaries to lexical subsections are \lx,
 \ps (\pn), \sn, \se. Each of these sections or subsections can take a full set of field
markers (except \lc and \hm, which should only occur at the top of the record).

Multiple parts of speech (\ps) are used to organize sections within an entry. A
lexeme that fills more than one syntactic slot (as a noun, verb, etc.) should not be
handled as homonyms. This is because the different syntactic functions (e.g.
'shower' (n) 'shower' (v) are still clearly related to each other in meaning.

From [Recommended Field Order](../markers/Order_of_Fields.md):

The following are all of the fields in their recommended order for a lexical entry. The order
shown here assumes you are using the standard hierarchy (the alternate hierarchy only varies
in the hierarchical order of the \sn, \se, and \ps fields). For more information on the alternate
hierarchy, see:

From [Using Subentries, Lexical Entries, and Minimal Entries](../markers/Using_Subentries_or_Lexical_Entries.md):

A common question that all lexicographers must face when wrestling with
complex (polymorphemic) lexemes is whether to incorporate them in the lexicon
as subentries under the lexical entry of their root lexeme, or to place them in the
lexicon as independent lexical entries. This is not an easy question to answer, but
it is addressed in greater detail in Chapter 4 (section 4.6) of the MDF field
manual (Coward and Grimes, 1995). For this database, we will summarize the two
options below:

Full discussions:

- [Sections in a Lexical Entry](../markers/Sections_in_a_Lexical_Entry.md)
- [Recommended Field Order](../markers/Order_of_Fields.md)
- [Using Subentries, Lexical Entries, and Minimal Entries](../markers/Using_Subentries_or_Lexical_Entries.md)
