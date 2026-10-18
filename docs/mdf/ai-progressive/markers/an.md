---
marker: [an]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [sy, lf]
tokens_estimate: 243
---


# \an antonym

*\key* \an

This field is used to reference an antonym of the lexeme.

MDF's standard printing adds the label "Ant: " to this field. 

Using the \lf (lexical function) field for this is a better practice. For example,

*\ftx*

```text
 \an sal
```

could be done instead as

*\ftx*

```text
 \lf Ant.
 \lv wrong, false
```

The latter gives more information to the outside reader by providing a gloss.
(National and regional glosses are available also.)

For more detailed information on this, see:

\cf \sy synonym

\cf \lf lexical function

*\typ* <Optional>

## Cross-references

- [sy](sy.md) sy synonym
- [lf](lf.md) lf lexical function label

## Semantics

Carries an antonym relating the entry to an opposite-meaning lexeme.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [sy](sy.md) sy synonym
