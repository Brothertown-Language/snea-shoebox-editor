#!/usr/bin/env python3
"""Convert the MDF 1.9a Toolbox field reference into JSON + LaTeX + HTML outputs.

Spec: .issues/1379/spec.md — Phases 1-3 (R-1..R-4, R-8; SC-13; SC-1/SC-3 renderers).

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
                                      The source's semantic chapter->marker
                                      grouping is expressed by cf cross-references
                                      (blocks[].targets); renderers should prefer
                                      that model for grouping.
    occurrence/duplicate            — duplicate-key handling: the first
                                      occurrence is the primary anchor
    preamble/blocks                 — raw lines (preamble as a list of raw
                                      lines before the first block; each block
                                      carries marker, text (marker line plus
                                      continuations, byte-for-byte), line, and
                                      for cf blocks targets (canonical keys
                                      resolved by whitespace-token exact lookup,
                                      accepting a leading "\\" and trailing
                                      "*.,;:"))

Renderers (presentation belongs here, never the parser):
- LaTeX: --latex PATH emits a book-class XeLaTeX document. Topics are emitted in
  the source's own navigation order — the home/TOC entry first, then each chapter
  in the home TOC (chapter_keys) order with its member markers in document order
  (topic_emission_order, mirroring the in-app MDF Reference page) — so the ToC
  and PDF bookmarks follow the source's hierarchy, not source-document order.
  Every one of the 108
  "\\key"+"\\shd" topics is an unnumbered \\chapter with \\label{key:<slug>} and a
  PDF bookmark; \\shd2/3/4 map to \\section/\\subsection/\\subsubsection; \\txt to
  body text; non-empty \\ftx and all \\fxv to byte-for-byte fancyvrb Verbatim
  blocks (no re-wrapping; long lines break visually via fvextra without altering
  characters); \\cf tokens to green hyperref links to the target topic's label
  (backslash-prefixed tokens that resolve to no topic render as a visible
  placeholder); \\nt to caption-size notes; \\typ to caption-size attribute
  lines; \\bib to hanging-indent bibliography entries; \\nwt to bulleted lists
  with the source's • characters preserved. Each rendered example block carries
  a "(N)" apparatus label (N = 1..444) so example-block counts are verifiable
  in pdftotext output; verbatim content itself is untouched.
- HTML: --html-dir DIR emits a multi-page static site: index.html (home entry
  "aa" plus the chapter TOC) and one page per chapter group. Sidebar navigation on every page
  (chapters in chapter_keys order), deep-linking anchors, vendored lunr.js search (assets/lunr.js,
  no CDN), @media print styles, responsive layout. Anchor scheme: every topic
  section carries id="key-<slug>" where <slug> is the exact \\key value with
  whitespace runs replaced by "-" (collision-safe by construction); \\cf links
  point at "<page>#key-<slug>".
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
# Shared emission order — the source's own navigation model
# ---------------------------------------------------------------------------


def topic_emission_order(document: dict) -> list[dict]:
    """Flat emission order mirroring the in-app MDF Reference browser tree
    (src/frontend/pages/mdf_reference.py _render_browser_tree): the home/TOC
    entry first, then each chapter topic in the home TOC (chapter_keys) order
    followed by its member markers (chapter == chapter_key, not is_chapter)
    in document order. Anything the grouping leaves unplaced keeps document
    order at the end, so no topic is dropped and none is duplicated."""
    topics = document["topics"]
    by_key: dict[str, list[dict]] = {}
    for topic in topics:
        by_key.setdefault(topic["key"], []).append(topic)
    ordered: list[dict] = []
    placed: set[int] = set()

    def place(topic: dict) -> None:
        if id(topic) not in placed:
            placed.add(id(topic))
            ordered.append(topic)

    for topic in by_key.get(document.get("home_key"), []):
        place(topic)
    for chapter_key in document.get("chapter_keys") or []:
        for topic in by_key.get(chapter_key, []):
            place(topic)
        for topic in topics:
            if topic.get("chapter") == chapter_key and not topic["is_chapter"]:
                place(topic)
    for topic in topics:
        place(topic)
    return ordered


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


LATEX_SECTION_COMMANDS = {"shd2": "\\section", "shd3": "\\subsection", "shd4": "\\subsubsection"}

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
\\definecolor{keycolor}{RGB}{110,110,110}
\\IfFontExistsTF{Noto Serif}{\\setmainfont{Noto Serif}}{%
\\IfFontExistsTF{Gentium Book Plus}{\\setmainfont{Gentium Book Plus}}{%
\\IfFontExistsTF{Gentium Plus}{\\setmainfont{Gentium Plus}}{%
\\IfFontExistsTF{Gentium}{\\setmainfont{Gentium}}{\\setmainfont{Latin Modern Roman}}}}}
\\IfFontExistsTF{Noto Sans Mono}{\\setmonofont{Noto Sans Mono}}{%
\\IfFontExistsTF{DejaVu Sans Mono}{\\setmonofont{DejaVu Sans Mono}}{\\setmonofont{Latin Modern Mono}}}
\\setcounter{secnumdepth}{-2}
\\setcounter{tocdepth}{0}
\\pagestyle{headings}
\\hypersetup{hidelinks,bookmarksnumbered=false,pdftitle={MDF Lexical Fields},pdfsubject={MDF 1.9a field documentation}}
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
            parts.append(latex_escape(chunk))
    tail = join_prose(lines[1:])
    if tail:
        parts.append(" " + latex_escape(tail))
    return "{\\color{cflink} " + "".join(parts).strip() + "}"


def latex_example(block: dict, number: int) -> str:
    content = "\n".join(block_lines(block))
    return (
        "{\\small\\color{exlabel}(" + str(number) + ")}\\par\n\\noindent\n"
        "\\begin{Verbatim}[fontsize=\\footnotesize,breaklines,breakanywhere]\n" + content + "\n\\end{Verbatim}"
    )


def latex_nwt_group(blocks: list[dict]) -> str:
    items = "\n".join("  \\item[] " + latex_escape(join_prose(block_lines(b))) for b in blocks)
    return "\\begin{itemize}\n" + items + "\n\\end{itemize}"


def latex_topic(topic: dict, slugs: dict[str, str], warnings: list[str], example_number: int) -> tuple[str, int]:
    key = topic["key"]
    slug = slugs[key]
    label = f"key:{slug}" if topic["occurrence"] == 1 else f"key:{slug}-{topic['occurrence']}"
    out = [f"\\chapter{{{latex_escape(topic['heading'] or key)}}}\\label{{{label}}}\n"]
    out.append("{\\small\\ttfamily\\color{keycolor} " + latex_escape("\\key " + key) + "}\\par\n")
    preamble = join_prose(topic["preamble"])
    if preamble:
        out.append(latex_escape(preamble) + "\n\n")
    nwt_group: list[dict] = []

    def flush_nwt() -> None:
        nonlocal nwt_group
        if nwt_group:
            out.append(latex_nwt_group(nwt_group) + "\n")
            nwt_group = []

    for block in topic["blocks"]:
        marker = block["marker"]
        if marker == "nwt":
            nwt_group.append(block)
            continue
        flush_nwt()
        if marker == "shd":
            continue
        if marker in LATEX_SECTION_COMMANDS:
            heading = latex_escape(join_prose(block_lines(block)))
            out.append(LATEX_SECTION_COMMANDS[marker] + "{" + heading + "}\n")
        elif marker == "txt":
            text = join_prose(block_lines(block))
            if text:
                out.append(latex_escape(text) + "\n\n")
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
                out.append("\\begin{quote}\\small\\itshape " + latex_escape(text) + "\\end{quote}\n")
        elif marker == "typ":
            text = join_prose(block_lines(block))
            if text:
                out.append("{\\small " + latex_escape(text) + "}\\par\n")
        elif marker == "bib":
            text = join_prose(block_lines(block))
            if text:
                out.append(
                    "{\\small\\setlength{\\parindent}{0pt}\\hangindent=3em\\hangafter=1 "
                    + latex_escape(text)
                    + "\\par}\n"
                )
    flush_nwt()
    return "\n".join(out), example_number


def render_latex(document: dict, out_path: str) -> list[str]:
    """Render the book-class XeLaTeX document per the Typographic Mapping table."""
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
    chunks.append("\\end{titlepage}\n\\tableofcontents\n\\mainmatter\n")
    example_number = 0
    for topic in topic_emission_order(document):
        body, example_number = latex_topic(topic, slugs, warnings, example_number)
        chunks.append(body + "\n")
    chunks.append("\\end{document}\n")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(chunks), encoding="utf-8", newline="\n")
    return warnings


# ---------------------------------------------------------------------------
# HTML renderer (R-4)
# ---------------------------------------------------------------------------

HTML_SECTION_LEVELS = {"shd2": "h3", "shd3": "h4", "shd4": "h5"}


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
.key-line { margin: 0.2rem 0 0.8rem; }
.key-line code { font-family: var(--mono); color: #555; font-size: 0.85rem; }
.section-heading { margin: 1.4rem 0 0.4rem; }
p.cf { color: var(--cf-green); }
a.cf-link { color: var(--cf-green); }
a.cf-missing { color: #a00000; border-bottom: 1px dotted #a00000; }
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
            parts.append(escaped)
    tail = join_prose(lines[1:])
    if tail:
        parts.append(" " + html_escape(tail))
    return "".join(parts).strip()


def html_nwt_group(blocks: list[dict]) -> str:
    items = "\n".join(f"  <li>{html_escape(join_prose(block_lines(b)))}</li>" for b in blocks)
    return '<ul class="nwt-list">\n' + items + "\n</ul>"


def html_topic(topic: dict, page_by_key: dict[str, str], slugs: dict[str, str], warnings: list[str]) -> str:
    key = topic["key"]
    out = [f'<section class="topic" id="key-{slugs[key]}">']
    out.append(f'  <h2 class="topic-heading">{html_escape(topic["heading"] or key)}</h2>')
    out.append(f'  <p class="key-line"><code>{html_escape("\\key " + key)}</code></p>')
    preamble = join_prose(topic["preamble"])
    if preamble:
        out.append(f"  <p>{html_escape(preamble)}</p>")
    nwt_group: list[dict] = []

    def flush_nwt() -> None:
        nonlocal nwt_group
        if nwt_group:
            out.append(html_nwt_group(nwt_group))
            nwt_group = []

    for block in topic["blocks"]:
        marker = block["marker"]
        if marker == "nwt":
            nwt_group.append(block)
            continue
        flush_nwt()
        if marker == "shd":
            continue
        if marker in HTML_SECTION_LEVELS:
            level = HTML_SECTION_LEVELS[marker]
            heading = html_escape(join_prose(block_lines(block)))
            out.append(f'  <{level} class="section-heading">{heading}</{level}>')
        elif marker == "txt":
            text = join_prose(block_lines(block))
            if text:
                out.append(f"  <p>{html_escape(text)}</p>")
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
                out.append(f'  <p class="note">{html_escape(text)}</p>')
        elif marker == "typ":
            text = join_prose(block_lines(block))
            if text:
                out.append(f'  <p class="typ">{html_escape(text)}</p>')
        elif marker == "bib":
            text = join_prose(block_lines(block))
            if text:
                out.append(f'  <p class="bib">{html_escape(text)}</p>')
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
    items = []
    home = next((t for t in document["topics"] if t["key"] == document["home_key"]), None)
    if home is not None:
        label = html_escape(home["heading"] or home["key"])
        items.append(f'  <li class="nav-home"><a href="index.html">{label}</a></li>')
    for chapter in (t for t in topic_emission_order(document) if t["is_chapter"]):
        page = page_by_key[chapter["key"]]
        label = html_escape(chapter["heading"] or chapter["key"])
        members = [t for t in document["topics"] if t["chapter"] == chapter["key"]]
        if members:
            inner = "\n".join(
                f'      <li><a href="{page}#key-{slugs[m["key"]]}">\\{html_escape(m["key"])}</a></li>' for m in members
            )
            items.append(
                f'  <li class="nav-chapter"><a href="{page}">{label}</a>\n    <ul>\n{inner}\n    </ul>\n  </li>'
            )
        else:
            items.append(f'  <li class="nav-chapter"><a href="{page}">{label}</a></li>')
    return "\n".join(items)


def render_html(document: dict, out_dir: str) -> list[str]:
    """Render the multi-page static site: index.html (home entry) plus one page per
    chapter group, with vendored-lunr search, deep-link anchors, and print CSS."""
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

    page_by_key: dict[str, str] = {}
    for topic in topics:
        if topic["key"] == document["home_key"] or (not topic["is_chapter"] and topic["chapter"] is None):
            page_by_key[topic["key"]] = "index.html"
        elif topic["is_chapter"]:
            page_by_key[topic["key"]] = f"{slugs[topic['key']]}.html"
        else:
            page_by_key[topic["key"]] = f"{slugs[topic['chapter']]}.html"

    version = (document["document_header"].get("title") or "").split()
    version_text = html_escape(version[0]) if version else "unknown"
    date = document["source"].get("git_last_modified") or "unknown date"
    nav = html_nav(document, page_by_key, slugs)
    home_topic = next((t for t in topics if t["key"] == document["home_key"]), None)

    chapter_links = "\n".join(
        f'    <li><a href="{page_by_key[c["key"]]}">{html_escape(c["heading"] or c["key"])}</a></li>'
        for c in (t for t in topic_emission_order(document) if t["is_chapter"])
    )
    chapter_index = (
        '<section class="chapter-index" id="chapters">\n  <h2 class="topic-heading">Chapters</h2>\n'
        "<ol>\n" + chapter_links + "\n</ol>\n</section>"
    )

    pages: dict[str, str] = {}
    index_content = []
    if home_topic is not None:
        index_content.append(html_topic(home_topic, page_by_key, slugs, warnings))
    index_content.append(chapter_index)
    pages["index.html"] = HTML_PAGE_TEMPLATE.format(
        page_title="Home", version=version_text, date=date, nav=nav, content="\n".join(index_content)
    )
    for chapter in (t for t in topics if t["is_chapter"]):
        members = [t for t in topics if t["chapter"] == chapter["key"]]
        content = [html_topic(chapter, page_by_key, slugs, warnings)]
        content.extend(html_topic(m, page_by_key, slugs, warnings) for m in members)
        pages[f"{slugs[chapter['key']]}.html"] = HTML_PAGE_TEMPLATE.format(
            page_title=html_escape(chapter["heading"] or chapter["key"]),
            version=version_text,
            date=date,
            nav=nav,
            content="\n".join(content),
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
