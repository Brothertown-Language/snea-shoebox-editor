---
marker: [sy]
category: <Optional>
hierarchy_level: any
concerns: [semantics]
cross_refs: [lf, cf, an]
tokens_estimate: 397
---


# \sy synonym

*\key* \sy

This and the \an (antonym) field are helpful for those who want to keep track of
such information without using the \lf structure.

But you are encouraged to use the \lf fields to handle "synonym" and "antonym"
cross-referencing (instead of the \sy and \an fields). This is because the \lf fields
allow for glossing of the reference, whereas \sy and \an do not. Glossing has the
advantage of giving the outside reader an idea of the meaning of a referenced
lexeme without actually having to go and look it up directly. For example, a
synonym of '-haw' ('to pound with a pestle') is '-tutu' ('to pound with a rock'). This
could be encoded in the '-haw' entry as:

*\ftx*

```text
 \sy -tutu
```

And would print as:

*\fxv*

```text
 Syn: -tutu.
```

But this tells the reader nothing really. Whereas if this were encoded as:

*\ftx*

```text
 \lf Syn
 \lv -tutu
 \le to pound with a rock
```

This would print as:

*\fxv*

```text
 Syn: -tutu 'to pound with a rock'.
```

Which, to the outsider using your dictionary, is far more helpful.

For related information, see:

\cf \lf and \cf 

See also:

\cf \an

*\typ* <Optional>

## Cross-references

- [lf](lf.md) lf lexical function label
- [cf](cf.md) cf confer/cross-reference
- [an](an.md) an antonym

## Semantics

Carries a synonym relating the entry to a same-meaning lexeme.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [an](an.md) an antonym
