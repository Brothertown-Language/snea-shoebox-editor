---
marker: [Alternate_Hierarchy]
category: topic
hierarchy_level: topic
concerns: [structure]
cross_refs: [Sections_in_a_Lexical_Entry, Order_of_Fields, Using_Subentries_or_Lexical_Entries]
tokens_estimate: 1175
---


# A Sense-Oriented Hierarchy

*\key* Alternate_Hierarchy

The alternative hierarchy that MDF supports differs from the standard hierarchy
in its ordering of these three crucial field markers: \sn \se \ps. (The standard
hierarchy expects the order \ps \sn \se.) The alternate hierarchy's ordering can be
outlined as follows: 

*\ftx*

```text
 \lx lexeme
 \sn sense number
 \se subentry
 \ps part-of-speech
 \ps part-of-speech
 \se subentry
 \ps part-of-speech
 \ps part-of-speech
 \sn sense number
 \se subentry
 \ps part-of-speech
 \ps part-of-speech
 \se subentry
 \ps part-of-speech
 \ps part-of-speech
```

The main purpose of this alternate hierarchy is to allow the user to group or base subentries on
a given sense. A simplified example of this would be:

*\ftx*

```text
 \lx adá
 \ge throw ; discard
```

 \sn 1

 \de throw

 \se mongadá

 \ps vt 

 \ge throw away ; discard

 \de throw something away; to discard

 \se iadá

 \ps vt

 \de throw something away

 \se paadá

 \mr po-adá 

 \ps vCAUS

 \de drop

 \se puadá-adá

 \mr pu-adá-adá

 \ps v

 \de throw away (thoughtlessly or irresponsibly)

 \sn 2

 \de divorce

 \se muadá

 \mr m-pu-adá

 \ps vREC

 \de divorce smb (lit. throw each other)

 \se puadá

 \mr pu-adá

 \ps vREC

 \de be divorced; separated (used for divorce and separation of man and wife)

 \sn 3

 \de defecate

 \se paadá

 \ps vCAUS

 \de defecate

This example would typically print as follows (shown without the character styles
here):

*\fxv*

```text
 adá throw, discard.
 1) throw.
 mongadá vt. throw something away; to discard. 
 iadá vt. throw something away.
 paadá Morf: po-adá. vCAUS. drop.
 puadá-adá v. throw away (thoughtlessly or irresponsibly).
 2) divorce.
 muadá Morf: m-pu-adá. vREC. divorce smb (lit. throw 
 each other).
 puadá Morf: pu-adá. vREC. be divorced; separated (used 
 for divorce and separation of man and wife). 
 3) defecate.
 paadá vCAUS. defecate.
```

Note that by judiciously using the definition (\de) field you can give labels to the sense
groupings. 

This method of organization was urgently requested by people working in languages that were
highly polymorphemic, because this hierarchy allows them to group complex polymorphemic
lexemes together based on a sense (rather than stand alone -- as subentries do in the standard
MDF hierarchy). 

*\nt* Currently MDF can only support one method of organization per lexical database. Therefore you
must choose which hierarchical method will best meet your needs and use only that one
method for all lexical entries in you dictionary. Mixing methods in Shoebox and MDF can
produce inaccurate interlinear choices and browse views, as well as odd formatting in the output.

To help with the decision, note that there are advantages and disadvantages to using this
alternate method:

*\nwt*  • One main advantage to this structure is that you can see all the related 
 polymorphemic forms that carry a particular sense. 

*\nwt*  • One disadvantage of this structure is that you do not readily see the actual 
 range of senses that a particular polymorphemic form can express.

For important information on how MDF handles sections in a lexical entry as well as related
information on the standard hierarchy, please see:

\cf Sections_in_a_Lexical_Entry

For information on the order in which fields are formatted for printing, see: 

\cf Order_of_Fields

To continue on with the general discussion, jump to:

\cf Using_Subentries_or_Lexical_Entries

Also see the document "MDF-ch2 revised.doc", pages 55-63 for a detailed
discussion of the two different hierarchies.

## Cross-references

- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry
- [Order_of_Fields](Order_of_Fields.md) Recommended Field Order
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries

## Structure

Documents the alternate hierarchy, in which senses precede subentries and parts of speech.

Listed under [Structure](../concerns/structure.md).

## Backlinks

- [aa](aa.md) Helps Database for MDF Marker Set
- [Order_of_Fields](Order_of_Fields.md) Recommended Field Order
- [Sections_in_a_Lexical_Entry](Sections_in_a_Lexical_Entry.md) Sections in a Lexical Entry
- [sn](sn.md) sn sense number
- [Using_Subentries_or_Lexical_Entries](Using_Subentries_or_Lexical_Entries.md) Using Subentries, Lexical Entries, and Minimal Entries
