---
marker: [re]
category: <Basic>
hierarchy_level: any
concerns: [semantics]
cross_refs: [ge]
tokens_estimate: 411
---


# \re reversal form (English)

*\key* \re

This gives the English word or phrase to be use to reverse the dictionary for an English index.
If an \re * is present, the relevant entry, subentry, or sense will be ignored (i.e. not included in
the reversed index). Like the \ge field, the data for this field can be kept each in its own field
or concatenated in one field, separated by ' ; '. 

It is often the case that there are several translation equivalents for a single vernacular term.
'huma' might mean 'house', 'hut', 'shack', 'dwelling', 'lean-to', etc. Each of these equivalents
would be good to have in the reversed index, e.g.:

*\ftx*

```text
 \re house ; hut ; shack ; dwelling ; lean-to
```

They could also be entered in separate \re fields. For more information on this, see:

\cf \ge gloss (English)

The advantage of keeping them in separate fields is that if you setup Toolbox to
sort on the \re fields (to get a type of finderlist), it will sort on all of them, but if
the reversal glosses are all concatenated, Toolbox will only index on the first
form.

*\nt* This field does not normally print in the dictionary.

*\typ* <Basic>

## Cross-references

- [ge](ge.md) ge gloss (English)

## Semantics

Carries the English reversal form from which finder lists are generated.

Listed under [Semantics](../concerns/semantics.md).

## Backlinks

- [ge](ge.md) ge gloss (English)
- [Introduction](Introduction.md) Standard Lexical Database Field Markers (for MDF)
- [rn](rn.md) rn reversal form (national)
