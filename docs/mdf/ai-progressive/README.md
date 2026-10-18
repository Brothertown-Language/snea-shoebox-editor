# MDF Field Documentation — AI Progressive Read

Progressive-read Markdown migrated from the frozen Toolbox source
`docs/mdf/MDFields19a_UTF8.txt` (MDF 1.9a, last modified 2006-05-12;
see `docs/mdf/SOURCE-PROVENANCE.md`). After migration these files are
the maintained source of truth; the Toolbox original stays frozen as
provenance.

## Entry points by intent

- Know the marker? `markers/{code}.md` — one file per `\key` entry
  (multi-code entries are one file listing all codes in `marker`).
- Browsing? [`index.md`](index.md) — every marker code linked, with
  one-line summaries.
- Job-framed? `concerns/` — structure, semantics, presentation, and
  data-handling views across all entries.
- Cross-cutting discussion? `topics/` — hierarchy variants, printing,
  character styles, range sets, old and changed markers.
- Agent routing card: `docs/agents/mdf-progressive.md` (repo root
  path).

## Frontmatter

Every `markers/{code}.md` carries:

- `marker` — the entry's code or codes (a reference to any code targets
  this file).
- `category` — the source's own `\typ` value (`Basic`, `Reserved`,
  `Optional`), `topic` for discussion entries; `null` where the source
  types the entry nowhere (`lx`, `xg`, the verb-paradigm entry).
- `hierarchy_level` — `topic` for discussion entries; `0` the record
  root `\lx`; `1` the part-of-speech section markers `\ps`/`\pn`; `2`
  the sense marker `\sn`; `3` the subentry marker `\se`; `record` for
  `\hm`/`\lc` (top of the record only); `any` for fields the source
  fixes no level for (every section takes a full field set).
- `concerns` — the concern views this entry participates in.
- `cross_refs` — entries this entry references (derived from `\cf`).
- `tokens_estimate` — this file's own token measure, ceil(bytes / 4).

## Conventions

- Source content is migrated with line structure preserved; horizontal
  whitespace runs normalize to single spaces (the comparison rule the
  migration acceptance uses). Examples (`\ftx`) and printed output
  (`\fxv`) render in fenced blocks; `\cf` lines stay verbatim and are
  additionally resolved as links in `## Cross-references`; targets list
  their referring entries under `## Backlinks`.
- Empty example fields (`\ftx` with no content — 11 in the source)
  render nothing.
- Token measure throughout: ceil(bytes / 4). Every file stays under
  4,000 tokens; the whole directory totals about 58,667 tokens.

## Generated file inventory

- `index.md`
- `markers/aa.md`
- `markers/Alternate_Hierarchy.md`
- `markers/an.md`
- `markers/bb.md`
- `markers/bw.md`
- `markers/ce.md`
- `markers/cf.md`
- `markers/Character_Style_Codes.md`
- `markers/cn.md`
- `markers/cr.md`
- `markers/de.md`
- `markers/dn.md`
- `markers/dr.md`
- `markers/dt.md`
- `markers/dv.md`
- `markers/ec.md`
- `markers/ee.md`
- `markers/eg.md`
- `markers/en.md`
- `markers/er.md`
- `markers/es.md`
- `markers/et.md`
- `markers/ev.md`
- `markers/Formatting_and_Printing.md`
- `markers/Free-form_Fields.md`
- `markers/ge.md`
- `markers/gn.md`
- `markers/gr.md`
- `markers/gv.md`
- `markers/hm.md`
- `markers/Introduction.md`
- `markers/is.md`
- `markers/lc.md`
- `markers/le.md`
- `markers/lf.md`
- `markers/ln.md`
- `markers/lr.md`
- `markers/lt.md`
- `markers/lv.md`
- `markers/lx.md`
- `markers/mn.md`
- `markers/mr.md`
- `markers/na.md`
- `markers/nd.md`
- `markers/ng.md`
- `markers/np.md`
- `markers/nq.md`
- `markers/ns.md`
- `markers/nt.md`
- `markers/oe.md`
- `markers/Old_and_Changed_Markers.md`
- `markers/on.md`
- `markers/or.md`
- `markers/Order_of_Fields.md`
- `markers/ov.md`
- `markers/pc.md`
- `markers/pd.md`
- `markers/pde.md`
- `markers/pdl.md`
- `markers/pdn.md`
- `markers/pdr.md`
- `markers/pdv.md`
- `markers/ph.md`
- `markers/pl.md`
- `markers/pn.md`
- `markers/Printed_Field_Labels.md`
- `markers/ps.md`
- `markers/Punctuation_and_Special_Codes.md`
- `markers/Range_Sets.md`
- `markers/rd.md`
- `markers/re.md`
- `markers/References.md`
- `markers/rf.md`
- `markers/rn.md`
- `markers/rr.md`
- `markers/sc.md`
- `markers/sd.md`
- `markers/se.md`
- `markers/Sections_in_a_Lexical_Entry.md`
- `markers/sg.md`
- `markers/sn.md`
- `markers/so.md`
- `markers/st.md`
- `markers/Summary_of_Fields.md`
- `markers/sy.md`
- `markers/tb.md`
- `markers/th.md`
- `markers/The_MDF_Documentation.md`
- `markers/ue.md`
- `markers/un.md`
- `markers/Unknown_Fields.md`
- `markers/ur.md`
- `markers/Using_Subentries_or_Lexical_Entries.md`
- `markers/uv.md`
- `markers/va.md`
- `markers/ve.md`
- `markers/vn.md`
- `markers/vr.md`
- `markers/we.md`
- `markers/When_MDF_Fails_to_Meet_Your_Requirements.md`
- `markers/wn.md`
- `markers/wr.md`
- `markers/xe.md`
- `markers/xg.md`
- `markers/xn.md`
- `markers/xr.md`
- `markers/xv.md`
- `markers/1s.md`
- `concerns/structure.md`
- `concerns/semantics.md`
- `concerns/presentation.md`
- `concerns/data-handling.md`
- `topics/hierarchy-standard.md`
- `topics/hierarchy-alternate.md`
- `topics/formatting-printing.md`
- `topics/character-styles.md`
- `topics/range-sets.md`
- `topics/old-changed-markers.md`
- `README.md`
