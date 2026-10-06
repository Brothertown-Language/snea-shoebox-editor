#!/usr/bin/env python3
"""Convert the MDF 1.9a Toolbox field reference into JSON + LaTeX + HTML outputs.

Spec: issue 1379 spec — Phases 1-3 (R-1..R-4, R-8; SC-13; SC-1/SC-3 renderers).

Parsing semantics (deterministic, line-anchored):
- A line opens a field record iff, at byte offset 0, it is "\\" plus one
  non-whitespace token plus whitespace or end-of-line, and the token is in
  MARKERS. Membership is an exact set lookup: "\\shd2" != "\\shd", and a glued
  token such as "\\shd2abc" is the single token "shd2abc" -> malformed path.
- Every other line (blank, indented, or non-marker) is a continuation of the
  current field, preserved byte-for-byte. No joining, stripping, or
  normalization happens here; renderers own presentation. Content is never
  regex-processed.
- An offset-0 "\\token" outside MARKERS emits a warning and is treated as
  continuation content (SC-13 malformed path).
- Zero "\\key" entries is a fatal error (R-8 fail-fast); no output file.

JSON schema (snea-mdf-master/1):
- source: path/sha256/bytes/lines provenance of the parsed file, plus
  `git_last_modified` (the source file's last-modified commit date as
  YYYY-MM-DD, from `git log -1 --format=%cs`; used by the LaTeX title block)
- document_header: the pre-first-key region ("\\_sh" title block and any
  sibling blocks), with `title` derived from the first "\\_sh" payload
- home_key: the source's built-in home/TOC entry ("aa", spec-pinned)
- chapter_keys: distinct cross-reference targets of the home entry, in the
  home entry's own reading order — the source's own chapter index
- warnings: malformed-marker and duplicate-key records (also echoed to stderr)
- topics: ordered by source position; each topic carries:
    key/key_text/line/index/heading — identity plus first "\\shd" payload
    is_chapter                      — key is one of chapter_keys
    chapter                         — document-order placement: key of the most
                                      recent preceding chapter topic (None for
                                      the home entry, for chapter topics
                                      themselves, and before the first chapter).
                                      Renderers regroup on top of this raw
                                      placement per the 2026-10-06 change control
                                      (book_structure).
    occurrence/duplicate            — duplicate-key handling: the first
                                      occurrence is the primary anchor
    preamble/blocks                 — raw lines (preamble as a list of raw
                                      lines before the first block; each block
                                      carries marker, text (marker line plus
                                      continuations, byte-for-byte), line, and
                                      for cf blocks targets (canonical keys
                                      resolved by whitespace-token exact lookup,
                                      accepting a leading "\\" and trailing
                                      "*.,;:")). cf blocks also carry pairs
                                      (2026-10-06 change control): the block's
                                      marker+gloss lookup pairs derived by
                                      presentation-level whitespace tokenization
                                      of the raw text — each token resolving
                                      through the target set starts a pair at
                                      parenthesis depth 0 (the 2026-10-06
                                      paren-depth rule: at depth >=1 a
                                      target-shaped token is gloss text of the
                                      currently-open pair, so a parenthetical
                                      cross-reference inside a gloss stays
                                      unsplit)
                                      {"target": canonical key, "gloss":
                                      intervening source words verbatim,
                                      "token": the source's own display token};
                                      punctuation-only tokens and the connective
                                      "and" in list position (directly after a
                                      bare target) are list structure between
                                      pairs, never gloss content. Additive only:
                                      targets and text are unchanged and the
                                      round-trip ignores pairs.

Renderers (presentation belongs here, never the parser):
- LaTeX: --latex PATH emits a book-class XeLaTeX document structured by the
  source's own navigation model (book_structure; 2026-10-06 change control):
  title page, then the Foreword (unnumbered \\chapter* with a ToC entry and PDF
  bookmark — AI-use disclosure and notes on changes relative to the source),
  then \\tableofcontents, then
  the home/TOC entry first as the opening chapter, then the 17 discussion
  chapters in the home TOC (chapter_keys) order with their internal \\shd2/3/4
  nesting, then the terminal "Field Marker Reference" apparatus chapter holding
  every single-marker definition topic as a \\subsection entry grouped by
  reference group (\\section: Record Marker / Basic Fields / Reserved Fields /
  Optional Fields / Discontinued — the group derived from each topic's own
  parsed data: \\lx is the Record Marker, a \\typ block value names
  Basic/Reserved/Optional, and the sole \\typ-less marker \\xg is Discontinued by
  its own heading wording), alphabetical by key within each group. The one
  multi-key topic ("Old verb paradigm markers") rides under Old_and_Changed_Markers
  per its own \\cf. Every one of the 108
  "\\key"+"\\shd" topics is unnumbered with \\label{key:<slug>} and a PDF
  bookmark; \\shd2/3/4 map to \\section/\\subsection/\\subsubsection (reference
  entries descend one ladder step further, so an entry's \\shd2 is a
  \\subsubsection); \\txt to
  body text; non-empty \\ftx and all \\fxv to byte-for-byte fancyvrb Verbatim
  blocks (no re-wrapping; long lines break visually via fvextra without altering
  characters); \\cf tokens to green hyperref links to the target topic's label
  (backslash-prefixed tokens that resolve to no topic render as a visible
  placeholder); cf blocks whose pairs carry a gloss render as a description
  list — one \\item per pair, the label a green hyperref link to the target
  anchor and the gloss body text whose own marker mentions render as green
  links to their topics (the 2026-10-06 paren-depth rule keeps
  cross-referenced markers inside the gloss they annotate) — with strictly
  consecutive glossed
  cf blocks coalesced into one list; bare-target cf blocks (all pairs
  glossless) keep the inline rendering; \\nt to caption-size notes; \\typ to
  caption-size attribute lines; \\bib to hanging-indent bibliography entries;
  \\nwt to bulleted lists
  with the source's • characters preserved. Each rendered example block carries
  a "(N)" apparatus label (N = 1..444) so example-block counts are verifiable
  in pdftotext output; verbatim content itself is untouched.
- HTML: --html-dir DIR emits a multi-page static site: index.html (home entry
  "aa" plus the chapter TOC and a Foreword link), foreword.html (the Foreword,
  first link in the sidebar navigation), one page per discussion chapter (the chapter's own
  content plus any non-reference member topics — for this source only the
  multi-key stub, under Old_and_Changed_Markers), and the terminal
  field-marker-reference.html holding the marker-definition entries in the same
  group/entry structure as the PDF. Sidebar navigation on every page (aa, the
  chapters in chapter_keys order, then the reference page with its groups and
  entries), deep-linking anchors, vendored lunr.js search (assets/lunr.js,
  no CDN), @media print styles, responsive layout. Anchor scheme: every topic
  section carries id="key-<slug>" where <slug> is the exact \\key value with
  whitespace runs replaced by "-" (collision-safe by construction); \\cf links
  point at "<page>#key-<slug>" — a marker entry's anchor name is unchanged by
  the regrouping, only the page carrying it moves.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "snea-mdf-master/1"
GENERATOR = "scripts/convert_mdf_master.py"
DEFAULT_SOURCE = "docs/mdf/MDFields19a_UTF8.txt"
DEFAULT_OUT = "docs/mdf/build/master.json"
DEFAULT_LATEX = "docs/mdf/build/master.tex"
DEFAULT_HTML_DIR = "docs/mdf/build/site"

MARKERS = frozenset(
    {
        "key",
        "shd",
        "shd2",
        "shd3",
        "shd4",
        "txt",
        "ftx",
        "fxv",
        "cf",
        "nt",
        "typ",
        "bib",
        "nwt",
        "_sh",
    }
)
TARGET_STRIP_CHARS = "*.,;:"
HOME_KEY = "aa"


def marker_token(line: str) -> str | None:
    if not line.startswith("\\"):
        return None
    rest = line[1:]
    end = 0
    while end < len(rest) and not rest[end].isspace():
        end += 1
    return rest[:end]


def field_payload(line: str, marker: str) -> str:
    payload = line[1 + len(marker) :]
    if payload[:1].isspace():
        payload = payload[1:]
    return payload


def first_line(text: str) -> str:
    return text.split("\n", 1)[0]


def cf_targets(marker_line: str, aliases: dict[str, str]) -> list[str]:
    targets: list[str] = []
    for token in field_payload(marker_line, "cf").split():
        candidate = token[1:] if token.startswith("\\") else token
        while candidate and candidate[-1] in TARGET_STRIP_CHARS:
            candidate = candidate[:-1]
        target = aliases.get(candidate)
        if target is not None and target not in targets:
            targets.append(target)
    return targets


def cf_pairs(text: str, aliases: dict[str, str]) -> list[dict]:
    """Derive a \\cf block's marker+gloss lookup pairs (2026-10-06 change control).

    Presentation-level whitespace tokenization of the block's raw text (the
    marker-line payload minus the marker token, plus every continuation line):
    each token resolving through the target set — exact set lookup, accepting a
    leading "\\" and trailing "*.,;:" exactly as cf_targets — starts a new pair
    ONLY at parenthesis depth 0 (2026-10-06 paren-depth rule); at depth >=1 a
    target-shaped token is gloss text of the currently-open pair, so a
    parenthetical cross-reference inside a gloss stays unsplit ("variant form
    (also ve* comments)" is one va pair, and ve* remains a link target without
    becoming a row). Depth is a plain character count over the non-target
    tokens ("(" increments, ")" decrements, floored at 0 so a stray close
    paren cannot corrupt the state); a target-shaped token can never carry a
    parenthesis character (the strip set never removes one), so its depth is
    exactly the scan state before it. Intervening words accumulate as the
    pair's gloss, joined with single spaces and trimmed. A punctuation-only
    token, or the connective "and", arriving while the current gloss is still
    empty is list structure between pairs — the serialization of a target
    list, not gloss content — so the bare connective case "\\xe, \\xn, and
    \\xr" yields all-empty glosses and no stored gloss is fragment-only; the
    same tokens arriving mid-gloss are gloss content and stay verbatim
    ("paradigm form & glosses)"). Every pair carries the source's own display
    token so renderers label the link exactly as the source row writes it
    (e.g. "ge*", "\\sy"). Tokens before the first pair have no pair to attach
    to (none occur in the source); raw text is preserved regardless. Content
    is never regex-processed.
    """
    lines = text.split("\n")
    tokens = [tok for chunk in [field_payload(lines[0], "cf"), *lines[1:]] for tok in chunk.split()]
    pairs: list[dict] = []
    depth = 0
    for tok in tokens:
        candidate = tok[1:] if tok.startswith("\\") else tok
        while candidate and candidate[-1] in TARGET_STRIP_CHARS:
            candidate = candidate[:-1]
        target = aliases.get(candidate)
        if target is not None:
            if depth == 0:
                pairs.append({"target": target, "gloss": "", "token": tok})
            elif pairs:
                current = pairs[-1]
                current["gloss"] = (current["gloss"] + " " + tok).strip()
            continue
        depth = max(0, depth + tok.count("(") - tok.count(")"))
        if pairs and not pairs[-1]["gloss"] and (
            not any(ch.isalnum() for ch in tok) or tok.lower() == "and"
        ):
            continue
        if pairs:
            current = pairs[-1]
            current["gloss"] = (current["gloss"] + " " + tok).strip()
    return pairs


def parse_mdf_text(text: str, source_path: str, git_last_modified: str | None = None) -> dict:
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    header_preamble: list[str] = []
    header_blocks: list[dict] = []
    raw_topics: list[dict] = []
    warnings: list[dict] = []
    current_topic: dict | None = None
    current_block: dict | None = None

    def warn(kind: str, lineno: int, detail: str) -> None:
        warnings.append({"kind": kind, "line": lineno, "detail": detail})
        print(f"warning: line {lineno}: {detail}", file=sys.stderr)

    for lineno, line in enumerate(lines, 1):
        token = marker_token(line)
        if token is not None and token in MARKERS:
            if token == "key":
                current_topic = {
                    "key": field_payload(line, "key"),
                    "key_text": line,
                    "line": lineno,
                    "blocks": [],
                    "preamble": [],
                }
                raw_topics.append(current_topic)
                current_block = None
            else:
                block = {"marker": token, "text": line, "line": lineno}
                if current_topic is None:
                    header_blocks.append(block)
                else:
                    current_topic["blocks"].append(block)
                current_block = block
            continue
        if token is not None:
            warn(
                "malformed_marker",
                lineno,
                f"marker \\{token} is outside the 14-marker whitelist; treating line as continuation content",
            )
        if current_block is not None:
            current_block["text"] += "\n" + line
        elif current_topic is not None:
            current_topic["preamble"].append(line)
        else:
            header_preamble.append(line)

    aliases: dict[str, str] = {}
    for topic in raw_topics:
        if topic["key"] and topic["key"] not in aliases:
            aliases[topic["key"]] = topic["key"]
    for topic in raw_topics:
        for part in topic["key"].split():
            if part and part not in aliases:
                aliases[part] = topic["key"]

    occurrences: dict[str, int] = {}
    for topic in raw_topics:
        occurrence = occurrences.get(topic["key"], 0) + 1
        occurrences[topic["key"]] = occurrence
        topic["occurrence"] = occurrence
        topic["duplicate"] = occurrence > 1
        if topic["duplicate"]:
            warn(
                "duplicate_key",
                topic["line"],
                f"key {topic['key']!r} already defined; occurrence {occurrence} is not the primary anchor",
            )

    for region in (header_blocks, *(topic["blocks"] for topic in raw_topics)):
        for block in region:
            if block["marker"] == "cf":
                block["targets"] = cf_targets(first_line(block["text"]), aliases)
                block["pairs"] = cf_pairs(block["text"], aliases)

    home = next((topic for topic in raw_topics if topic["key"] == HOME_KEY), None)
    chapter_keys: list[str] = []
    if home is not None:
        for block in home["blocks"]:
            if block["marker"] == "cf":
                for target in block["targets"]:
                    if target not in chapter_keys:
                        chapter_keys.append(target)
    chapter_set = set(chapter_keys)

    topics: list[dict] = []
    last_chapter: str | None = None
    for index, topic in enumerate(raw_topics):
        is_chapter = topic["key"] in chapter_set
        if is_chapter:
            chapter = None
            last_chapter = topic["key"]
        else:
            chapter = last_chapter
        heading = next(
            (field_payload(first_line(block["text"]), "shd") for block in topic["blocks"] if block["marker"] == "shd"),
            None,
        )
        topics.append(
            {
                "key": topic["key"],
                "key_text": topic["key_text"],
                "line": topic["line"],
                "index": index,
                "heading": heading,
                "is_chapter": is_chapter,
                "chapter": chapter,
                "occurrence": topic["occurrence"],
                "duplicate": topic["duplicate"],
                "preamble": topic["preamble"],
                "blocks": topic["blocks"],
            }
        )

    title = next(
        (field_payload(first_line(block["text"]), "_sh") for block in header_blocks if block["marker"] == "_sh"),
        None,
    )

    return {
        "schema": SCHEMA,
        "generator": GENERATOR,
        "source": {
            "path": source_path,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "bytes": len(text.encode("utf-8")),
            "lines": len(lines),
            "git_last_modified": git_last_modified,
        },
        "document_header": {
            "preamble": header_preamble,
            "title": title,
            "blocks": header_blocks,
        },
        "home_key": home["key"] if home is not None else None,
        "chapter_keys": chapter_keys,
        "warnings": warnings,
        "topics": topics,
    }


def summarize(document: dict, out_path: str) -> str:
    cf_count = sum(1 for topic in document["topics"] for block in topic["blocks"] if block["marker"] == "cf")
    examples = sum(
        1
        for topic in document["topics"]
        for block in topic["blocks"]
        if block["marker"] == "fxv" or (block["marker"] == "ftx" and first_line(block["text"]).rstrip() != "\\ftx")
    )
    return (
        f"wrote {out_path}: {len(document['topics'])} topics, "
        f"{cf_count} cf fields, {examples} examples, "
        f"{len(document['warnings'])} warnings"
    )


# ---------------------------------------------------------------------------
# Shared rendering helpers — presentation decisions live here, never in the parser
# ---------------------------------------------------------------------------


def block_lines(block: dict) -> list[str]:
    """Marker-line payload plus continuation lines, in source order."""
    lines = block["text"].split("\n")
    return [field_payload(lines[0], block["marker"]), *lines[1:]]


def is_example(block: dict) -> bool:
    """SC-14 example rule: non-empty \\ftx (first line carries more than the bare
    marker) or any \\fxv. Mirrors summarize(); the 11 whitespace-only \\ftx blocks
    are source structure, not examples."""
    if block["marker"] == "ftx":
        return block["text"].split("\n", 1)[0].rstrip() != "\\ftx"
    return True


def join_prose(lines: list[str]) -> str:
    """Join hard-wrapped prose lines into flowing text: whitespace runs collapse to
    single spaces, except a line ending in "-" joined directly to a following word
    (hyphenated compounds such as "free-" / "form" must not gain a space)."""
    parts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if parts and parts[-1].endswith("-") and stripped[:1].isalnum():
            parts[-1] += stripped
        else:
            parts.append(stripped)
    return " ".join(parts)


QUOTE_FORMS = {
    "latex": {"open_double": "``", "close_double": "''", "open_single": "`", "close_single": "'"},
    "unicode": {"open_double": "“", "close_double": "”", "open_single": "‘", "close_single": "’"},
}
_CLOSING_QUOTE_CONTEXT = frozenset(".,;:!?)]_-}")
_QUOTE_CHARS = frozenset("\"'")


def _quote_closes(text: str, i: int) -> bool:
    """Look-behind-only classification of the straight quote at index i: True
    when it is a closing quote. Bounded backward scan — every decision reads
    only characters at positions < i; no lookahead, no pairing state, no
    alternation counting."""
    previous = text[i - 1] if i else ""
    if previous.isalnum() or previous in _CLOSING_QUOTE_CONTEXT:
        return True
    # Refined pair window (corpus census 2026-10-06, source pinned MDF 1.9a):
    # a pair whose closing quote is pad-separated from its item — reading
    # backward from this quote Q: one space, a run of one or more item chars
    # (non-whitespace, non-quote), then optionally exactly one space, then a
    # straight quote O — puts a space before Q, so the preceding-character
    # rule alone mis-opens it (corpus instances: the padded literals ' ; ',
    # ' } ', ' f '; the hug-right sequences ', ' and '; '; the quoted labels
    # "Ant: " style). Q closes its pair only when O itself classifies as an
    # OPENER under this same look-behind rule (equivalently the base rule on
    # every corpus instance): in the 12 sequences the unconditioned window
    # would also match, O is immediately preceded by an alphanumeric and so
    # is a closer — the pair reading fails and the condition excludes every
    # one. A chained third quote (its own putative pair-opener already
    # classified closing) fails the opener check and keeps the base opening
    # behavior — pairing would be required to do better on synthetic
    # three-quote runs such as "' a ' b ' c", and the corpus contains none.
    if i < 4 or text[i - 1] != " ":
        return False
    k = i - 2
    while k >= 0 and not text[k].isspace() and text[k] not in _QUOTE_CHARS:
        k -= 1
    if i - 2 == k:
        return False
    j = k - 1 if (k >= 0 and text[k] == " ") else k
    if j < 0 or text[j] not in _QUOTE_CHARS:
        return False
    return not _quote_closes(text, j)


def shape_quotes(text: str, form: str = "unicode") -> str:
    """Deterministic typographic quote shaping (developer directive, 2026-10-06):
    a look-behind quote shaper, no regex on content. A straight " or ' is the
    CLOSING form when its preceding character is alphanumeric, or is one of
    ".", ",", ";", ":", "!", "?", ")", "]", "_", "-", or "}" — American
    typesetting places sentence punctuation inside the quotes, so a quote
    directly after punctuation is a closing quote, and the offline corpus
    census of master.json prose paths (2026-10-06, design evidence only)
    shows "_", "-", and "}" immediately before a straight quote only where
    that quote closes a quoted token ('_', '-', and " |fl{ }"); any other
    preceding character — whitespace, string/line start ("\\n" is whitespace,
    so a line start is opening context), "(", or anything else — is the
    OPENING form. The decision is look-behind only: a bounded backward scan
    with no lookahead, no pairing memory, and no alternation counting;
    ambiguous classes observed in the corpus keep the current behavior (a
    quote after "(" opens — 13/13 word-initial instances; a quote after
    whitespace or string start opens — 262/262 instances).
    Refined pair window (corpus census 2026-10-06, source pinned MDF 1.9a):
    a pair whose closing quote is pad-separated from its item — reading
    backward from a straight quote Q: one space, a run of one or more item
    chars (non-whitespace, non-quote), then optionally exactly one space,
    then a straight quote O — puts a space before Q, so the
    preceding-character rule alone mis-opens it. Corpus instances: the
    padded literals ' ; ' (ge/gn/gr/re/rn), ' } ' (Character_Style_Codes),
    ' f ' (Summary_of_Fields); the hug-right sequences ', ' (ge/gn/gr) and
    '; ' (lf); and the quoted labels "Ant: "-style (23 instances). Q CLOSES
    its pair only when O itself classifies as an OPENER under this same
    look-behind rule (equivalently the base rule on every corpus instance):
    census total exactly 34 window matches, zero counterexamples corpus-wide
    — the 12 sequences the unconditioned window would also match (e.g.
    "'-nya' means 'his' 'hers' or 'its'") all have O immediately preceded by
    an alphanumeric, so O is a closer, the pair reading fails, and the
    opener condition excludes every one. The window is exact: whitespace
    other than a space terminates the item run without counting as pad,
    wider padding ("'  x  '") or a second pad space stays with the base
    rule, and a three-quote chain's third quote (its own putative
    pair-opener already classified closing) fails the opener check and keeps
    the base opening behavior — pairing would be required to do better on
    synthetic three-quote runs such as "' a ' b ' c", and the corpus
    contains none. Already-curly input (U+2018/2019/201C/201D) holds
    no straight quotes and passes through unchanged, so the unicode form is
    idempotent. Presentation only: applied exclusively on prose rendering
    paths (\\txt, \\nt, \\bib, \\typ, \\shd topic headings, cf pair glosses,
    bare-target cf display text, and the authored Foreword) — never to
    \\ftx/\\fxv verbatim blocks (they depict literal database input and stay
    byte-exact) and never to master.json. form "latex" emits TeX quote
    ligatures for the XeLaTeX output; form "unicode" emits the typographic
    characters directly (HTML).
    """
    shapes = QUOTE_FORMS[form]
    out: list[str] = []
    for i, ch in enumerate(text):
        if ch in _QUOTE_CHARS:
            if _quote_closes(text, i):
                out.append(shapes["close_double" if ch == '"' else "close_single"])
            else:
                out.append(shapes["open_double" if ch == '"' else "open_single"])
        else:
            out.append(ch)
    return "".join(out)


def latex_prose(text: str) -> str:
    """LaTeX prose register: shape quotes to TeX ligatures first — the lookback
    must see the source's own characters — then escape; the inserted `` `` ''
    ` ' ligature characters are not LaTeX specials and pass through
    latex_escape unchanged."""
    return latex_escape(shape_quotes(text, "latex"))


def html_prose(text: str) -> str:
    """HTML prose register: shape quotes to their Unicode forms, then escape."""
    return html_escape(shape_quotes(text, "unicode"))


def cf_segments(payload: str, targets: list[str]) -> list[tuple[str, str, str | None]]:
    """Split a \\cf first-line payload into (kind, token, canonical) segments,
    consuming the block's parsed targets in order. A backslash-prefixed token that
    resolves to no topic is a "missing" placeholder (edge case); plain words are
    description text."""
    segments: list[tuple[str, str, str | None]] = []
    remaining = list(targets)
    for chunk in re.findall(r"\S+|\s+", payload):
        if chunk.isspace():
            segments.append(("space", chunk, None))
            continue
        candidate = chunk[1:] if chunk.startswith("\\") else chunk
        while candidate and candidate[-1] in TARGET_STRIP_CHARS:
            candidate = candidate[:-1]
        if candidate in remaining:
            remaining.remove(candidate)
            segments.append(("link", chunk, candidate))
        elif chunk.startswith("\\"):
            segments.append(("missing", chunk, candidate))
        else:
            segments.append(("text", chunk, None))
    return segments


def split_ws_runs(text: str) -> list[tuple[bool, str]]:
    """Whitespace-run-preserving tokenization, no regex on content: a plain
    character scan yields (is_whitespace, chunk) pairs covering the input
    exactly, so renderers can rewrite individual tokens while every other
    character (all whitespace runs included) passes through verbatim."""
    runs: list[tuple[bool, str]] = []
    i = 0
    length = len(text)
    while i < length:
        j = i
        if text[j].isspace():
            while j < length and text[j].isspace():
                j += 1
            runs.append((True, text[i:j]))
        else:
            while j < length and not text[j].isspace():
                j += 1
            runs.append((False, text[i:j]))
        i = j
    return runs


def gloss_segments(gloss: str, keys) -> list[tuple[str, str, str | None]]:
    """Split a pair gloss into (kind, chunk, canonical) segments covering the
    string exactly (2026-10-06 paren-depth change control). Whitespace runs
    and non-mention text stay verbatim; each whitespace-delimited token whose
    candidate — leading backslash stripped, trailing "*.,;:" stripped, the
    same normalization the targets logic uses — is a known topic key (exact
    set lookup) becomes a "mention" segment carrying that key, which the
    renderers turn into a live link. Punctuation is not part of the strip set,
    so a resolving token never contains parenthesis characters and the gloss's
    own parenthetical structure is untouched."""
    segments: list[tuple[str, str, str | None]] = []
    for is_space, chunk in split_ws_runs(gloss):
        if is_space:
            segments.append(("space", chunk, None))
            continue
        candidate = chunk[1:] if chunk.startswith("\\") else chunk
        while candidate and candidate[-1] in TARGET_STRIP_CHARS:
            candidate = candidate[:-1]
        if candidate in keys:
            segments.append(("mention", chunk, candidate))
        else:
            segments.append(("text", chunk, None))
    return segments


def build_slugs(topics: list[dict]) -> dict[str, str]:
    """Stable anchor slugs: the exact \\key value with whitespace runs replaced by
    "-"; a numeric suffix guards against hypothetical collisions."""
    slugs: dict[str, str] = {}
    used: set[str] = set()
    for topic in topics:
        key = topic["key"]
        if key in slugs:
            continue
        base = re.sub(r"\s+", "-", key.strip()) or "key"
        slug, n = base, 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        slugs[key] = slug
    return slugs


def render_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)
    print(f"warning: {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# cf lookup pairs — description-list rendering (2026-10-06 change control)
# ---------------------------------------------------------------------------


def pair_is_glossed(pair: dict) -> bool:
    """A pair is glossed iff its gloss carries alphanumeric content. The
    derivation never stores punctuation-only or connective-position fragments,
    so this is the whole predicate."""
    return any(ch.isalnum() for ch in pair.get("gloss", ""))


def cf_block_glossed(block: dict) -> bool:
    """A cf block renders as a description list iff ≥1 pair is glossed; blocks
    whose pairs are all glossless (bare target lists, prose connectives) keep
    the inline rendering."""
    return any(pair_is_glossed(pair) for pair in block.get("pairs") or [])


def coalesce_cf_blocks(blocks: list[dict]) -> list[tuple[str, list[dict]]]:
    """Presentation grouping shared by all three renderers: a maximal run of
    strictly consecutive cf blocks that ALL carry ≥1 glossed pair becomes one
    ("list", run) group — rendered as a single description list; every other
    block is a ("single", [block]) group rendered by the per-block rules."""
    groups: list[tuple[str, list[dict]]] = []
    i = 0
    while i < len(blocks):
        block = blocks[i]
        if block["marker"] == "cf" and cf_block_glossed(block):
            run = [block]
            j = i + 1
            while j < len(blocks) and blocks[j]["marker"] == "cf" and cf_block_glossed(blocks[j]):
                run.append(blocks[j])
                j += 1
            groups.append(("list", run))
            i = j
        else:
            groups.append(("single", [block]))
            i += 1
    return groups


# ---------------------------------------------------------------------------
# Shared book structure — the source's own navigation model
# (2026-10-06 change control: issue 1379 spec)
# ---------------------------------------------------------------------------

REFERENCE_GROUP_ORDER = ("record", "basic", "reserved", "optional", "discontinued")
REFERENCE_GROUP_TITLES = {
    "record": "Record Marker",
    "basic": "Basic Fields",
    "reserved": "Reserved Fields",
    "optional": "Optional Fields",
    "discontinued": "Discontinued",
}
REFERENCE_PAGE = "field-marker-reference.html"
REFERENCE_CHAPTER_TITLE = "Field Marker Reference"
FOREWORD_PAGE = "foreword.html"
FOREWORD_TITLE = "Foreword"


def is_reference_entry(topic: dict, home_key: str | None) -> bool:
    """A single-marker definition topic: not the home entry, not a chapter topic,
    and a \\key naming exactly one marker (no internal whitespace). The multi-key
    "Old verb paradigm markers" stub is excluded here — placement_chapter rides
    it under Old_and_Changed_Markers per its own \\cf."""
    return not topic["is_chapter"] and topic["key"] != home_key and " " not in topic["key"].strip()


def reference_group(topic: dict) -> str:
    """Deterministic reference group from the topic's own parsed data: \\lx is the
    record marker (the SF catalog's own "RECORD MARKER" section); otherwise the
    \\typ block value (<Basic>/<Reserved>/<Optional>); a single-marker topic with
    no \\typ block is \\xg, discontinued by its own heading wording."""
    if topic["key"] == "lx":
        return "record"
    typ = next((block for block in topic["blocks"] if block["marker"] == "typ"), None)
    if typ is not None:
        first = typ["text"].split("\n", 1)[0]
        if "<Basic>" in first:
            return "basic"
        if "<Reserved>" in first:
            return "reserved"
        if "<Optional>" in first:
            return "optional"
    return "discontinued"


def placement_chapter(topic: dict, chapter_keys: list[str]) -> str | None:
    """Chapter a non-chapter topic renders under. Default is the document-order
    chapter; a multi-key topic instead follows its own \\cf when that names a
    chapter topic (the source's placement for the numeric stub: "See the topic
    Old_and_Changed_Markers")."""
    if " " in topic["key"].strip():
        for block in topic["blocks"]:
            if block["marker"] == "cf":
                for target in block.get("targets", []):
                    if target in chapter_keys:
                        return target
    return topic["chapter"]


def book_structure(document: dict) -> dict:
    """The book's semantic structure, derived entirely from the parsed topics:
    the home entry first; then the discussion chapters in home-TOC (chapter_keys)
    order, each followed by its non-reference member topics in document order;
    then the terminal reference groups with their single-marker entries
    alphabetical by key. Anything the grouping leaves unplaced keeps document
    order in "residual" (empty for the 1.9a source), so no topic is dropped and
    none is duplicated."""
    topics = document["topics"]
    home_key = document.get("home_key")
    chapter_keys: list[str] = document.get("chapter_keys") or []

    def first_by_key(key: str | None) -> dict | None:
        if key is None:
            return None
        return next((topic for topic in topics if topic["key"] == key), None)

    home = first_by_key(home_key)
    chapters: list[tuple[dict, list[dict]]] = []
    placed: set[int] = {id(home)} if home is not None else set()
    for chapter_key in chapter_keys:
        chapter = first_by_key(chapter_key)
        if chapter is None:
            continue
        placed.add(id(chapter))
        members = [
            topic
            for topic in topics
            if not topic["is_chapter"]
            and topic["key"] != home_key
            and not is_reference_entry(topic, home_key)
            and placement_chapter(topic, chapter_keys) == chapter_key
        ]
        placed.update(id(member) for member in members)
        chapters.append((chapter, members))

    reference: dict[str, list[dict]] = {}
    for topic in topics:
        if is_reference_entry(topic, home_key):
            placed.add(id(topic))
            reference.setdefault(reference_group(topic), []).append(topic)
    residual = [topic for topic in topics if id(topic) not in placed]
    groups = {
        group: sorted(reference[group], key=lambda t: t["key"])
        for group in REFERENCE_GROUP_ORDER
        if group in reference
    }
    return {"home": home, "chapters": chapters, "residual": residual, "reference": groups}


# ---------------------------------------------------------------------------
# Foreword — AI-use disclosure and transformation notes (issue #1379 directive,
# 2026-10-06). One canonical text; each renderer adapts it to its own register.
# ---------------------------------------------------------------------------

FOREWORD_PARAGRAPHS = (
    "This reference presents the MDF 1.9a field documentation in a printable, browsable form. "
    "The source document is a Toolbox/Shoebox help file — a flat collection of records "
    "designed for on-screen keyword search rather than linear reading. The source identifies "
    "itself as draft version 1.9a (May 12, 2006); the original database was constructed by "
    "David Coward and the revisions by Karen Buseman.",
    "This edition was assembled with the assistance of AI. An automated conversion pipeline "
    "(a Python parser, XeLaTeX typesetting, and static HTML generation), designed and "
    "implemented by an AI agent under human direction and review, transformed the source "
    "into the present formats. All field content is preserved from the source without "
    "alteration; the AI's role was structural and typographic, not editorial. No content was "
    "invented, paraphrased, or omitted.",
)
FOREWORD_CHANGES_LEAD = "Changes made relative to the source:"
FOREWORD_CHANGES = (
    "Table of contents. The source has no print-style table of contents; its navigation is a "
    "cross-reference table on the home record plus keyword search. This edition adds a proper "
    "ToC. The chapter order follows the source's own recommended reading order: the topics "
    "listed on the home record, in the order it presents them.",
    "Unified field reference. The field-marker records, which the source interleaves "
    "alphabetically for on-screen lookup, are collected into a single Field Marker Reference "
    "section, grouped by the source's own field classifications — the record marker, Basic "
    "fields, Reserved fields, Optional fields (as defined in the source's Introduction), and "
    "Discontinued markers — alphabetical within each group. One obsolete-marker record is "
    "placed with the discussion of old and changed markers, as its own cross-reference directs.",
    'Cross-references ("See also") render as live links, set in green following the source\'s '
    "own stated convention.",
    "Formatting and printing examples are reproduced verbatim in monospaced blocks.",
    "Typography, page layout, bookmarks, pagination, and typographic quotation marks are new to "
    "this edition; the text itself is unchanged. Formatting examples keep the source's literal "
    "straight quotes, as they depict exact database input.",
)
FOREWORD_COLOPHON = (
    "Typeset with XeLaTeX (Noto Serif, with Gentium). "
    "HTML edition generated from the same parsed source.",
    "Conversion of 2026-10-06. Assembled with AI assistance — OpenCode "
    "(huggingface/zai-org/GLM-5.3-Flash), directed by Michael Conrad.",
)


def latex_foreword() -> str:
    """Front-matter Foreword as an unnumbered chapter with a ToC entry and PDF
    bookmark, placed before \\tableofcontents."""
    parts = [
        "\\clearpage\n\\phantomsection\n\\addcontentsline{toc}{chapter}{" + FOREWORD_TITLE + "}\n",
        "\\chapter*{" + FOREWORD_TITLE + "}\n",
    ]
    for paragraph in FOREWORD_PARAGRAPHS:
        parts.append(latex_prose(paragraph) + "\n\n")
    parts.append(latex_prose(FOREWORD_CHANGES_LEAD) + "\n\\begin{enumerate}\n")
    for change in FOREWORD_CHANGES:
        parts.append("  \\item " + latex_prose(change) + "\n")
    parts.append("\\end{enumerate}\n\n")
    for paragraph in FOREWORD_COLOPHON:
        parts.append(latex_escape(paragraph) + "\n\n")
    return "".join(parts)


def html_foreword_content() -> str:
    """The Foreword page body: heading, paragraphs, the numbered changes list,
    and the colophon, in the site's standard topic styling."""
    out = ['<section class="topic foreword" id="foreword">']
    out.append(f'  <h2 class="topic-heading">{html_escape(FOREWORD_TITLE)}</h2>')
    for paragraph in FOREWORD_PARAGRAPHS:
        out.append(f"  <p>{html_prose(paragraph)}</p>")
    out.append(f"  <p>{html_prose(FOREWORD_CHANGES_LEAD)}</p>")
    out.append('  <ol>')
    for change in FOREWORD_CHANGES:
        out.append(f"    <li>{html_prose(change)}</li>")
    out.append("  </ol>")
    for paragraph in FOREWORD_COLOPHON:
        out.append(f"  <p>{html_escape(paragraph)}</p>")
    out.append("</section>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# LaTeX renderer (R-3; Typographic Mapping table)
# ---------------------------------------------------------------------------

LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_LATEX_SPECIAL_RE = re.compile("[" + re.escape("".join(LATEX_SPECIALS)) + "]")


def latex_escape(text: str) -> str:
    return _LATEX_SPECIAL_RE.sub(lambda match: LATEX_SPECIALS[match.group()], text)


LATEX_HEADING_LADDER = ["\\chapter", "\\section", "\\subsection", "\\subsubsection", "\\paragraph", "\\subparagraph"]

LATEX_PREAMBLE = """% !TEX program = xelatex
% !TEX encoding = UTF-8 Unicode
% Generated by scripts/convert_mdf_master.py from the MDF 1.9a source; do not edit.
\\documentclass[10pt,openany]{book}
\\usepackage{fontspec}
\\usepackage{geometry}
\\usepackage{xcolor}
\\usepackage{fancyvrb}
\\usepackage{fvextra}
\\usepackage{hyperref}
\\geometry{margin=25mm}
\\definecolor{cflink}{RGB}{0,110,0}
\\definecolor{cfmissing}{RGB}{170,0,0}
\\definecolor{exlabel}{RGB}{110,110,110}
\\IfFontExistsTF{Noto Serif}{\\setmainfont{Noto Serif}}{%
\\IfFontExistsTF{Gentium Book Plus}{\\setmainfont{Gentium Book Plus}}{%
\\IfFontExistsTF{Gentium Plus}{\\setmainfont{Gentium Plus}}{%
\\IfFontExistsTF{Gentium}{\\setmainfont{Gentium}}{\\setmainfont{Latin Modern Roman}}}}}
\\IfFontExistsTF{Noto Sans Mono}{\\setmonofont{Noto Sans Mono}}{%
\\IfFontExistsTF{DejaVu Sans Mono}{\\setmonofont{DejaVu Sans Mono}}{\\setmonofont{Latin Modern Mono}}}
\\setcounter{secnumdepth}{-2}
\\setcounter{tocdepth}{0}
\\pagestyle{headings}
\\hypersetup{hidelinks,bookmarksnumbered=false,bookmarksdepth=2,
pdftitle={MDF Lexical Fields},pdfsubject={MDF 1.9a field documentation}}
"""


def latex_cf(block: dict, slugs: dict[str, str], warnings: list[str], where: str) -> str:
    lines = block_lines(block)
    parts: list[str] = []
    for kind, chunk, canonical in cf_segments(lines[0], block.get("targets", [])):
        if kind == "space":
            parts.append(" ")
        elif kind == "link":
            parts.append(f"\\hyperref[key:{slugs[canonical]}]{{{latex_escape(chunk)}}}")
        elif kind == "missing":
            render_warning(
                warnings,
                f"cross-reference token {chunk!r} in {where} resolves to no topic; rendering placeholder",
            )
            parts.append("\\textcolor{cfmissing}{" + latex_escape(f"[{chunk}]") + "}")
        else:
            parts.append(latex_prose(chunk))
    tail = join_prose(lines[1:])
    if tail:
        parts.append(" " + latex_prose(tail))
    return "{\\color{cflink} " + "".join(parts).strip() + "}"


def latex_gloss(gloss: str, slugs: dict[str, str]) -> str:
    """A pair gloss with its own marker mentions as live links (2026-10-06
    paren-depth change control): each mention chunk renders as a green
    hyperref link to its topic's anchor; every other character — text and
    whitespace runs alike — passes through escaped-but-verbatim, with quote
    shaping on the text chunks (mention chunks stay byte-exact; chunks are
    whitespace-delimited, so per-chunk lookback matches whole-string
    lookback)."""
    parts: list[str] = []
    for kind, chunk, canonical in gloss_segments(gloss, slugs):
        if kind == "mention":
            parts.append(
                "\\hyperref[key:"
                + slugs[canonical]
                + "]{\\textcolor{cflink}{"
                + latex_escape(chunk)
                + "}}"
            )
        else:
            parts.append(latex_prose(chunk))
    return "".join(parts)


def latex_cf_list(blocks: list[dict], slugs: dict[str, str]) -> str:
    """A coalesced run of glossed cf blocks as one description list (2026-10-06
    change control): one \\item per lookup pair — the label a green hyperref
    link to the target topic's anchor carrying the source's own display token,
    the gloss body text with its own marker mentions as green links. Glossless
    pairs render as label-only rows."""
    items: list[str] = []
    for block in blocks:
        for pair in block.get("pairs") or []:
            slug = slugs[pair["target"]]
            label = latex_escape(pair.get("token") or pair["target"])
            item = "\\item[{\\hyperref[key:" + slug + "]{\\textcolor{cflink}{" + label + "}}}]"
            if pair["gloss"]:
                item += " " + latex_gloss(pair["gloss"], slugs)
            items.append(item)
    return "\\begin{description}\n" + "\n".join(items) + "\n\\end{description}"


def latex_example(block: dict, number: int) -> str:
    content = "\n".join(block_lines(block))
    return (
        "{\\small\\color{exlabel}(" + str(number) + ")}\\par\n\\noindent\n"
        "\\begin{Verbatim}[fontsize=\\footnotesize,breaklines,breakanywhere]\n" + content + "\n\\end{Verbatim}"
    )


def latex_nwt_group(blocks: list[dict]) -> str:
    items = "\n".join("  \\item[] " + latex_escape(join_prose(block_lines(b))) for b in blocks)
    return "\\begin{itemize}\n" + items + "\n\\end{itemize}"


def latex_topic(
    topic: dict, slugs: dict[str, str], warnings: list[str], example_number: int, level: int = 0
) -> tuple[str, int]:
    """Render one topic. level is the LaTeX heading level of the topic itself:
    0 = \\chapter (home entry and discussion chapters, plus multi-key stubs) and
    2 = \\subsection (Field Marker Reference entries). Internal \\shd2/3/4 blocks
    descend the heading ladder from there, so a reference entry's \\shd2 becomes
    a \\subsubsection."""
    key = topic["key"]
    slug = slugs[key]
    label = f"key:{slug}" if topic["occurrence"] == 1 else f"key:{slug}-{topic['occurrence']}"
    heading_text = latex_escape(shape_quotes(topic["heading"] or key, "latex"))
    out = [f"{LATEX_HEADING_LADDER[level]}{{{heading_text}}}\\label{{{label}}}\n"]
    preamble = join_prose(topic["preamble"])
    if preamble:
        out.append(latex_escape(preamble) + "\n\n")
    nwt_group: list[dict] = []

    def flush_nwt() -> None:
        nonlocal nwt_group
        if nwt_group:
            out.append(latex_nwt_group(nwt_group) + "\n")
            nwt_group = []

    for kind, run in coalesce_cf_blocks(topic["blocks"]):
        block = run[0]
        marker = block["marker"]
        if marker == "nwt":
            nwt_group.append(block)
            continue
        flush_nwt()
        if kind == "list":
            out.append(latex_cf_list(run, slugs) + "\n\n")
            continue
        if marker == "shd":
            continue
        if marker in ("shd2", "shd3", "shd4"):
            heading = latex_escape(shape_quotes(join_prose(block_lines(block)), "latex"))
            depth = int(marker[3]) - 2
            command = LATEX_HEADING_LADDER[min(level + 1 + depth, len(LATEX_HEADING_LADDER) - 1)]
            out.append(command + "{" + heading + "}\n")
        elif marker == "txt":
            text = join_prose(block_lines(block))
            if text:
                out.append(latex_prose(text) + "\n\n")
        elif marker in ("ftx", "fxv"):
            if marker == "ftx" and not is_example(block):
                continue
            example_number += 1
            out.append(latex_example(block, example_number) + "\n")
        elif marker == "cf":
            out.append(latex_cf(block, slugs, warnings, f"topic {key}") + "\n\n")
        elif marker == "nt":
            text = join_prose(block_lines(block))
            if text:
                out.append("\\begin{quote}\\small\\itshape " + latex_prose(text) + "\\end{quote}\n")
        elif marker == "typ":
            text = join_prose(block_lines(block))
            if text:
                out.append("{\\small " + latex_prose(text) + "}\\par\n")
        elif marker == "bib":
            text = join_prose(block_lines(block))
            if text:
                out.append(
                    "{\\small\\setlength{\\parindent}{0pt}\\hangindent=3em\\hangafter=1 "
                    + latex_prose(text)
                    + "\\par}\n"
                )
    flush_nwt()
    return "\n".join(out), example_number


def render_latex(document: dict, out_path: str) -> list[str]:
    """Render the book-class XeLaTeX document per the Typographic Mapping table:
    home entry, discussion chapters in home-TOC order, then the terminal Field
    Marker Reference chapter grouping the marker-definition entries."""
    warnings: list[str] = []
    topics = document["topics"]
    slugs = build_slugs(topics)
    title = "MDF Lexical Fields"
    raw_title = document["document_header"].get("title") or ""
    version = latex_escape(raw_title.split()[0]) if raw_title.split() else "unknown"
    date = document["source"].get("git_last_modified") or "unknown date"

    chunks = [LATEX_PREAMBLE, "\\begin{document}\n\\frontmatter\n\\begin{titlepage}\n\\centering\n"]
    chunks.append("{\\Huge " + title + "\\par}\n\\vspace{1.5em}\n")
    chunks.append("{\\large Version " + version + "\\par}\n\\vspace{0.5em}\n")
    chunks.append("{\\large " + date + "\\par}\n\\vspace{2em}\n")
    chunks.append(
        "{\\small Generated from \\texttt{"
        + latex_escape(document["source"]["path"])
        + "} (MDF 1.9a field documentation).\\par}\n"
    )
    chunks.append("\\end{titlepage}\n")
    chunks.append(latex_foreword())
    chunks.append("\\tableofcontents\n\\mainmatter\n")
    structure = book_structure(document)
    example_number = 0

    def emit(topic: dict, level: int = 0) -> None:
        nonlocal example_number
        body, example_number = latex_topic(topic, slugs, warnings, example_number, level)
        chunks.append(body + "\n")

    if structure["home"] is not None:
        emit(structure["home"])
    for chapter, members in structure["chapters"]:
        emit(chapter)
        for member in members:
            emit(member)
    for topic in structure["residual"]:
        emit(topic)
    if structure["reference"]:
        chunks.append("\\chapter{" + REFERENCE_CHAPTER_TITLE + "}\n")
        for group, entries in structure["reference"].items():
            chunks.append("\\section{" + REFERENCE_GROUP_TITLES[group] + "}\n")
            for entry in entries:
                emit(entry, level=2)
    chunks.append("\\end{document}\n")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(chunks), encoding="utf-8", newline="\n")
    return warnings


# ---------------------------------------------------------------------------
# HTML renderer (R-4)
# ---------------------------------------------------------------------------

HTML_SECTION_MARKERS = ("shd2", "shd3", "shd4")


def html_escape(text: str) -> str:
    return html.escape(text, quote=False)


HTML_STYLE = """/* MDF Lexical Fields — static reference site (generated) */
:root {
  --cf-green: #067d06;
  --mono: ui-monospace, "DejaVu Sans Mono", Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Noto Serif", Georgia, "Times New Roman", serif;
  line-height: 1.55;
  color: #1a1a1a;
  background: #fff;
}
.layout { display: flex; min-height: 100vh; }
.sidebar {
  flex: 0 0 300px;
  width: 300px;
  padding: 1rem;
  border-right: 1px solid #ddd;
  background: #fafaf8;
  font-size: 0.9rem;
  position: sticky;
  top: 0;
  max-height: 100vh;
  overflow-y: auto;
}
.side-title { font-weight: bold; margin: 0 0 0.25rem; }
.side-title a { text-decoration: none; color: inherit; }
.side-version { color: #666; font-size: 0.8rem; margin: 0 0 1rem; }
.search input {
  width: 100%;
  padding: 0.4rem;
  border: 1px solid #bbb;
  border-radius: 4px;
  font: inherit;
}
.search-results {
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 0.3rem;
  background: #fff;
  max-height: 50vh;
  overflow-y: auto;
}
.search-results a {
  display: block;
  padding: 0.3rem 0.5rem;
  text-decoration: none;
  border-bottom: 1px solid #eee;
}
.search-results a:hover { background: #eef6ee; }
.hit-key { font-family: var(--mono); color: var(--cf-green); margin-right: 0.5em; }
.hit-heading { color: #333; }
.search-empty { padding: 0.4rem 0.5rem; color: #666; }
.nav { list-style: none; margin: 0.75rem 0 0; padding: 0; }
.nav-chapter { margin: 0.35rem 0; }
.nav-chapter > a { font-weight: 600; text-decoration: none; color: #1a3a6b; }
.nav-chapter > ul { list-style: none; margin: 0.15rem 0 0.35rem; padding-left: 1rem; }
.nav-chapter > ul a {
  text-decoration: none;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: #333;
}
.nav a:hover { text-decoration: underline; }
.nav-home a { text-decoration: none; color: #1a3a6b; font-weight: 600; }
.nav-group { margin: 0.35rem 0; }
.nav-group > a { font-weight: 600; text-decoration: none; color: #1a3a6b; }
.nav-group > ul { list-style: none; margin: 0.15rem 0 0.35rem; padding-left: 1rem; }
.nav-group > ul a {
  text-decoration: none;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: #333;
}
.content { margin: 0; padding: 2rem 3rem; max-width: 52rem; }
.crumbs { font-size: 0.85rem; color: #666; margin-top: 0; }
.crumbs a { color: #1a3a6b; text-decoration: none; }
.topic { margin-bottom: 2.5rem; }
.topic-heading {
  font-size: 1.35rem;
  margin: 0;
  border-bottom: 2px solid #444;
  padding-bottom: 0.2rem;
}
.section-heading { margin: 1.4rem 0 0.4rem; }
p.cf { color: var(--cf-green); }
a.cf-link { color: var(--cf-green); }
a.cf-missing { color: #a00000; border-bottom: 1px dotted #a00000; }
dl.mdf-cf-list { margin: 0.3rem 0 0.9rem; }
dl.mdf-cf-list dt { font-weight: bold; }
dl.mdf-cf-list dd { margin: 0 0 0.25rem 2rem; }
pre.example {
  background: #f5f5f2;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.6rem 0.8rem;
  overflow-x: auto;
  font-family: var(--mono);
  font-size: 0.85rem;
  line-height: 1.35;
}
p.note {
  font-size: 0.85rem;
  color: #444;
  border-left: 3px solid #bbb;
  padding-left: 0.6rem;
  font-style: italic;
}
p.typ { font-size: 0.85rem; color: #555; }
p.bib { font-size: 0.9rem; padding-left: 2em; text-indent: -2em; }
ul.nwt-list { list-style: none; padding-left: 1.2rem; }
.chapter-index ol { padding-left: 1.5rem; }
.foreword ol { padding-left: 1.5rem; }
.foreword-link { margin: 0 0 1.5rem; }
.foreword-link a { color: #1a3a6b; }
@media (max-width: 900px) {
  .layout { display: block; }
  .sidebar {
    position: static;
    width: auto;
    max-height: none;
    border-right: none;
    border-bottom: 1px solid #ddd;
  }
  .content { padding: 1rem; max-width: none; }
}
@media print {
  .sidebar { display: none; }
  .content { margin: 0; padding: 0; max-width: none; }
  pre.example { white-space: pre-wrap; border: none; background: none; }
  p.cf, a.cf-link { color: var(--cf-green); }
  .crumbs { display: none; }
  body { font-size: 10.5pt; }
}
"""

HTML_SEARCH_JS = """/* MDF Lexical Fields client-side search (generated).
 * Index data: assets/search-index.js (window.MDF_SEARCH_INDEX, works from file://)
 * backed by assets/search-index.json. Pipeline: lunr defaults minus the stemmer,
 * stop-word, and trimmer filters so accented source characters (á, ñ, é) survive
 * tokenization unchanged. */
(function () {
  "use strict";
  var input = document.getElementById("mdf-search");
  var box = document.getElementById("mdf-search-results");
  if (!input || !box) return;
  var index = null;
  var docs = {};

  function loadIndex() {
    if (typeof window.MDF_SEARCH_INDEX !== "undefined") {
      return Promise.resolve(window.MDF_SEARCH_INDEX);
    }
    return fetch("assets/search-index.json").then(function (r) { return r.json(); });
  }

  loadIndex()
    .then(function (data) {
      data.forEach(function (d) { docs[d.id] = d; });
      index = lunr(function () {
        this.pipeline.remove(lunr.stemmer);
        this.pipeline.remove(lunr.stopWordFilter);
        this.pipeline.remove(lunr.trimmer);
        this.ref("id");
        this.field("key", { boost: 10 });
        this.field("heading", { boost: 5 });
        this.field("text");
        data.forEach(function (d) { this.add(d); }, this);
      });
    })
    .catch(function () {
      box.hidden = false;
      box.textContent = "Search index unavailable.";
    });

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(runSearch, 120);
  });

  function runSearch() {
    var query = input.value.trim();
    box.innerHTML = "";
    if (!query || !index) { box.hidden = true; return; }
    var hits;
    try { hits = index.search(query).slice(0, 25); } catch (err) { hits = []; }
    box.hidden = false;
    if (!hits.length) {
      var none = document.createElement("div");
      none.className = "search-empty";
      none.textContent = "No matches.";
      box.appendChild(none);
      return;
    }
    hits.forEach(function (hit) {
      var doc = docs[hit.ref];
      if (!doc) return;
      var link = document.createElement("a");
      link.href = doc.page + "#" + doc.anchor;
      var key = document.createElement("span");
      key.className = "hit-key";
      key.textContent = "\\\\" + doc.key;
      var heading = document.createElement("span");
      heading.className = "hit-heading";
      heading.textContent = doc.heading;
      link.appendChild(key);
      link.appendChild(heading);
      box.appendChild(link);
    });
  }

  document.addEventListener("click", function (event) {
    if (!box.contains(event.target) && event.target !== input) box.hidden = true;
  });
  input.addEventListener("keydown", function (event) {
    if (event.key === "Escape") { box.hidden = true; input.blur(); }
  });
})();
"""


def html_cf(block: dict, page_by_key: dict[str, str], slugs: dict[str, str], warnings: list[str], where: str) -> str:
    lines = block_lines(block)
    parts: list[str] = []
    for kind, chunk, canonical in cf_segments(lines[0], block.get("targets", [])):
        escaped = html_escape(chunk)
        if kind == "space":
            parts.append(" ")
        elif kind == "link":
            parts.append(f'<a class="cf-link" href="{page_by_key[canonical]}#key-{slugs[canonical]}">{escaped}</a>')
        elif kind == "missing":
            render_warning(
                warnings,
                f"cross-reference token {chunk!r} in {where} resolves to no topic; rendering placeholder",
            )
            parts.append(f'<a class="cf-missing" title="cross-reference target not found in source">{escaped}</a>')
        else:
            parts.append(html_prose(chunk))
    tail = join_prose(lines[1:])
    if tail:
        parts.append(" " + html_prose(tail))
    return "".join(parts).strip()


def html_gloss(gloss: str, page_by_key: dict[str, str], slugs: dict[str, str]) -> str:
    """A pair gloss with its own marker mentions as live links (2026-10-06
    paren-depth change control): each mention chunk renders as a
    class="cf-link" anchor to its topic's page anchor; every other character —
    text and whitespace runs alike — passes through escaped-but-verbatim, with
    quote shaping on the text chunks (mention chunks stay byte-exact; chunks
    are whitespace-delimited, so per-chunk lookback matches whole-string
    lookback)."""
    parts: list[str] = []
    for kind, chunk, canonical in gloss_segments(gloss, slugs):
        if kind == "mention":
            parts.append(
                f'<a class="cf-link" href="{page_by_key[canonical]}#key-{slugs[canonical]}">{html_escape(chunk)}</a>'
            )
        else:
            parts.append(html_prose(chunk))
    return "".join(parts)


def html_cf_list(blocks: list[dict], page_by_key: dict[str, str], slugs: dict[str, str]) -> str:
    """A coalesced run of glossed cf blocks as one description list (2026-10-06
    change control): <dt> the target link carrying the source's own display
    token, <dd> the gloss beside it — one row per pair, glossless pairs as
    empty rows. Marker mentions inside the gloss render as cf-links to their
    own topics."""
    rows: list[str] = []
    for block in blocks:
        for pair in block.get("pairs") or []:
            target = pair["target"]
            href = f"{page_by_key[target]}#key-{slugs[target]}"
            label = html_escape(pair.get("token") or target)
            rows.append(f'    <dt><a class="cf-link" href="{href}">{label}</a></dt>')
            rows.append(f"    <dd>{html_gloss(pair['gloss'], page_by_key, slugs)}</dd>")
    return '<dl class="mdf-cf-list">\n' + "\n".join(rows) + "\n</dl>"


def html_nwt_group(blocks: list[dict]) -> str:
    items = "\n".join(f"  <li>{html_escape(join_prose(block_lines(b)))}</li>" for b in blocks)
    return '<ul class="nwt-list">\n' + items + "\n</ul>"


def html_heading_tag(level: int) -> str:
    """Heading tag for a semantic level (2 = topic heading on a chapter page,
    3 = \\shd2 there); capped at h6."""
    return f"h{min(level, 6)}"


def html_topic(
    topic: dict, page_by_key: dict[str, str], slugs: dict[str, str], warnings: list[str], offset: int = 0
) -> str:
    """Render one topic section. offset demotes the heading levels for topics
    nested inside the Field Marker Reference page: an entry's own heading drops
    to h4 and its \\shd2 "Hint"/"Tip" blocks to h5, mirroring the LaTeX
    \\subsection/\\subsubsection levels."""
    key = topic["key"]
    heading_tag = html_heading_tag(2 + offset)
    heading_text = html_escape(shape_quotes(topic["heading"] or key, "unicode"))
    out = [f'<section class="topic" id="key-{slugs[key]}">']
    out.append(f'  <{heading_tag} class="topic-heading">{heading_text}</{heading_tag}>')
    preamble = join_prose(topic["preamble"])
    if preamble:
        out.append(f"  <p>{html_escape(preamble)}</p>")
    nwt_group: list[dict] = []

    def flush_nwt() -> None:
        nonlocal nwt_group
        if nwt_group:
            out.append(html_nwt_group(nwt_group))
            nwt_group = []

    for kind, run in coalesce_cf_blocks(topic["blocks"]):
        block = run[0]
        marker = block["marker"]
        if marker == "nwt":
            nwt_group.append(block)
            continue
        flush_nwt()
        if kind == "list":
            out.append("  " + html_cf_list(run, page_by_key, slugs))
            continue
        if marker == "shd":
            continue
        if marker in HTML_SECTION_MARKERS:
            level = html_heading_tag(int(marker[3]) + 1 + offset)
            heading = html_escape(shape_quotes(join_prose(block_lines(block)), "unicode"))
            out.append(f'  <{level} class="section-heading">{heading}</{level}>')
        elif marker == "txt":
            text = join_prose(block_lines(block))
            if text:
                out.append(f"  <p>{html_prose(text)}</p>")
        elif marker in ("ftx", "fxv"):
            if marker == "ftx" and not is_example(block):
                continue
            content = html_escape("\n".join(block_lines(block)))
            out.append(f'  <pre class="example mdf-example"><code>{content}</code></pre>')
        elif marker == "cf":
            body = html_cf(block, page_by_key, slugs, warnings, f"topic {key}")
            out.append(f'  <p class="cf">{body}</p>')
        elif marker == "nt":
            text = join_prose(block_lines(block))
            if text:
                out.append(f'  <p class="note">{html_prose(text)}</p>')
        elif marker == "typ":
            text = join_prose(block_lines(block))
            if text:
                out.append(f'  <p class="typ">{html_prose(text)}</p>')
        elif marker == "bib":
            text = join_prose(block_lines(block))
            if text:
                out.append(f'  <p class="bib">{html_prose(text)}</p>')
    flush_nwt()
    out.append("</section>")
    return "\n".join(out)


HTML_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title} — MDF Lexical Fields</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="layout">
<nav class="sidebar" aria-label="Reference navigation">
<p class="side-title"><a href="index.html">MDF Lexical Fields</a></p>
<p class="side-version">{version} · {date}</p>
<div class="search">
<input id="mdf-search" type="search" placeholder="Search topics…" autocomplete="off" aria-label="Search the reference">
<div id="mdf-search-results" class="search-results" hidden></div>
</div>
<ul class="nav">
{nav}
</ul>
</nav>
<main class="content">
{content}
</main>
</div>
<script src="assets/lunr.js"></script>
<script src="assets/search-index.js"></script>
<script src="assets/search.js"></script>
</body>
</html>
"""


def html_nav(document: dict, page_by_key: dict[str, str], slugs: dict[str, str]) -> str:
    """Sidebar: home entry, the discussion chapters in home-TOC order (with any
    non-reference members — the multi-key stub under Old_and_Changed_Markers),
    then the Field Marker Reference page with its group/entry structure."""
    structure = book_structure(document)
    items = [f'  <li class="nav-foreword"><a href="{FOREWORD_PAGE}">{FOREWORD_TITLE}</a></li>']
    home = structure["home"]
    if home is not None:
        label = html_escape(home["heading"] or home["key"])
        items.append(f'  <li class="nav-home"><a href="index.html">{label}</a></li>')
    for chapter, members in structure["chapters"]:
        page = page_by_key[chapter["key"]]
        label = html_escape(chapter["heading"] or chapter["key"])
        if members:
            inner = "\n".join(
                f'      <li><a href="{page}#key-{slugs[m["key"]]}">\\{html_escape(m["key"])}</a></li>' for m in members
            )
            items.append(
                f'  <li class="nav-chapter"><a href="{page}">{label}</a>\n    <ul>\n{inner}\n    </ul>\n  </li>'
            )
        else:
            items.append(f'  <li class="nav-chapter"><a href="{page}">{label}</a></li>')
    if structure["reference"]:
        group_items = []
        for group, entries in structure["reference"].items():
            entry_links = "\n".join(
                f'        <li><a href="{REFERENCE_PAGE}#key-{slugs[e["key"]]}">\\{html_escape(e["key"])}</a></li>'
                for e in entries
            )
            group_items.append(
                f'      <li class="nav-group"><a href="{REFERENCE_PAGE}#group-{group}">'
                f"{REFERENCE_GROUP_TITLES[group]}</a>\n"
                f"        <ul>\n{entry_links}\n        </ul>\n      </li>"
            )
        items.append(
            f'  <li class="nav-chapter"><a href="{REFERENCE_PAGE}">{REFERENCE_CHAPTER_TITLE}</a>\n    <ul>\n'
            + "\n".join(group_items)
            + "\n    </ul>\n  </li>"
        )
    return "\n".join(items)


def render_html(document: dict, out_dir: str) -> list[str]:
    """Render the multi-page static site: index.html (home entry), one page per
    discussion chapter (own content plus non-reference members), and the terminal
    Field Marker Reference page, with vendored-lunr search, deep-link anchors,
    and print CSS."""
    warnings: list[str] = []
    out = Path(out_dir)
    assets = out / "assets"
    lunr_path = assets / "lunr.js"
    if not lunr_path.is_file():
        raise RuntimeError(
            f"vendored lunr.js missing at {lunr_path}; the HTML renderer requires the committed "
            "vendor file (no CDN). See docs/mdf/build/site/assets/PROVENANCE.md."
        )
    assets.mkdir(parents=True, exist_ok=True)
    topics = document["topics"]
    slugs = build_slugs(topics)
    structure = book_structure(document)

    page_by_key: dict[str, str] = {}
    if structure["home"] is not None:
        page_by_key[structure["home"]["key"]] = "index.html"
    for topic in structure["residual"]:
        page_by_key.setdefault(topic["key"], "index.html")
    for chapter, members in structure["chapters"]:
        chapter_page = f"{slugs[chapter['key']]}.html"
        page_by_key.setdefault(chapter["key"], chapter_page)
        for member in members:
            page_by_key.setdefault(member["key"], chapter_page)
    for entries in structure["reference"].values():
        for entry in entries:
            page_by_key.setdefault(entry["key"], REFERENCE_PAGE)

    version = (document["document_header"].get("title") or "").split()
    version_text = html_escape(version[0]) if version else "unknown"
    date = document["source"].get("git_last_modified") or "unknown date"
    nav = html_nav(document, page_by_key, slugs)
    home_topic = structure["home"]

    chapter_links = "\n".join(
        f'    <li><a href="{page_by_key[chapter["key"]]}">{html_escape(chapter["heading"] or chapter["key"])}</a></li>'
        for chapter, _members in structure["chapters"]
    )
    chapter_index = (
        '<section class="chapter-index" id="chapters">\n  <h2 class="topic-heading">Chapters</h2>\n'
        "<ol>\n" + chapter_links + "\n</ol>\n</section>"
    )

    pages: dict[str, str] = {}
    foreword_link = f'<p class="foreword-link"><a href="{FOREWORD_PAGE}">{FOREWORD_TITLE}</a></p>'
    index_content = [foreword_link]
    if home_topic is not None:
        index_content.append(html_topic(home_topic, page_by_key, slugs, warnings))
    index_content.append(chapter_index)
    index_content.extend(html_topic(topic, page_by_key, slugs, warnings) for topic in structure["residual"])
    pages["index.html"] = HTML_PAGE_TEMPLATE.format(
        page_title="Home", version=version_text, date=date, nav=nav, content="\n".join(index_content)
    )
    for chapter, members in structure["chapters"]:
        content = [html_topic(chapter, page_by_key, slugs, warnings)]
        content.extend(html_topic(member, page_by_key, slugs, warnings) for member in members)
        pages[f"{slugs[chapter['key']]}.html"] = HTML_PAGE_TEMPLATE.format(
            page_title=html_escape(chapter["heading"] or chapter["key"]),
            version=version_text,
            date=date,
            nav=nav,
            content="\n".join(content),
        )

    pages[FOREWORD_PAGE] = HTML_PAGE_TEMPLATE.format(
        page_title=FOREWORD_TITLE,
        version=version_text,
        date=date,
        nav=nav,
        content=html_foreword_content(),
    )

    if structure["reference"]:
        reference_content = [f'<h2 class="topic-heading">{REFERENCE_CHAPTER_TITLE}</h2>']
        for group, entries in structure["reference"].items():
            reference_content.append(
                f'<h3 class="section-heading" id="group-{group}">{REFERENCE_GROUP_TITLES[group]}</h3>'
            )
            reference_content.extend(
                html_topic(entry, page_by_key, slugs, warnings, offset=2) for entry in entries
            )
        pages[REFERENCE_PAGE] = HTML_PAGE_TEMPLATE.format(
            page_title=REFERENCE_CHAPTER_TITLE,
            version=version_text,
            date=date,
            nav=nav,
            content="\n".join(reference_content),
        )

    search_docs = []
    for topic in topics:
        texts = [topic["heading"] or topic["key"]]
        for block in topic["blocks"]:
            if block["marker"] in ("txt", "nt", "typ", "bib", "nwt", "cf"):
                texts.append(join_prose(block_lines(block)))
        search_docs.append(
            {
                "id": topic["key"],
                "key": topic["key"],
                "heading": topic["heading"] or topic["key"],
                "page": page_by_key[topic["key"]],
                "anchor": f"key-{slugs[topic['key']]}",
                "text": " ".join(t for t in texts if t),
            }
        )
    index_json = json.dumps(search_docs, ensure_ascii=False, indent=2) + "\n"
    (assets / "search-index.json").write_text(index_json, encoding="utf-8", newline="\n")
    (assets / "search-index.js").write_text(
        "window.MDF_SEARCH_INDEX = " + index_json.rstrip() + "\n", encoding="utf-8", newline="\n"
    )
    (assets / "style.css").write_text(HTML_STYLE, encoding="utf-8", newline="\n")
    (assets / "search.js").write_text(HTML_SEARCH_JS, encoding="utf-8", newline="\n")

    for stale in out.glob("*.html"):
        if stale.name not in pages:
            stale.unlink()
    for name, content in pages.items():
        (out / name).write_text(content, encoding="utf-8", newline="\n")
    return warnings


def git_last_modified(source: str) -> str | None:
    """Last-modified commit date (YYYY-MM-DD) of the source file, for the title block."""
    path = Path(source).resolve()
    root = path.parent
    while root != root.parent and not (root / ".git").exists():
        root = root.parent
    if not (root / ".git").exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%cs", "--", str(path.relative_to(root))],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return proc.stdout.strip() or None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert the MDF 1.9a Toolbox field reference to JSON, LaTeX, and HTML outputs."
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE, help=f"source .txt file (default: {DEFAULT_SOURCE})")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"output JSON path (default: {DEFAULT_OUT})")
    parser.add_argument("--latex", metavar="PATH", help="also render a XeLaTeX document to this path")
    parser.add_argument("--html-dir", metavar="DIR", help="also render the multi-page HTML site into this directory")
    parser.add_argument(
        "--source-date",
        metavar="YYYY-MM-DD",
        help="source last-modified date for the LaTeX title block (default: git log of the source file)",
    )
    args = parser.parse_args(argv)

    source = Path(args.source)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        print(f"error: cannot read source {args.source}: {exc}", file=sys.stderr)
        return 2
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"error: source {args.source} is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    git_date = args.source_date or git_last_modified(args.source)
    document = parse_mdf_text(text, args.source, git_date)
    if not document["topics"]:
        print(
            f"error: source {args.source} contains zero \\key entries; nothing to convert (fail-fast per R-8)",
            file=sys.stderr,
        )
        return 2

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    out.write_text(payload, encoding="utf-8", newline="\n")

    render_warnings: list[str] = []
    if args.latex:
        render_warnings.extend(render_latex(document, args.latex))
    if args.html_dir:
        render_warnings.extend(render_html(document, args.html_dir))
    for message in render_warnings:
        print(f"warning: {message}", file=sys.stderr)

    summary = summarize(document, args.out)
    if args.latex:
        summary += f"; latex -> {args.latex}"
    if args.html_dir:
        summary += f"; html -> {args.html_dir}"
    if render_warnings:
        summary += f"; {len(render_warnings)} renderer warning(s)"
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
