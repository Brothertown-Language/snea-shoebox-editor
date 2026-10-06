#!/usr/bin/env python3
"""Convert the MDF 1.9a Toolbox field reference into a JSON intermediate representation.

Spec: .issues/1379/spec.md — Phase 1 (R-1, R-2, R-8; SC-13).

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
- source: path/sha256/bytes/lines provenance of the parsed file
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
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "snea-mdf-master/1"
GENERATOR = "scripts/convert_mdf_master.py"
DEFAULT_SOURCE = "docs/mdf/MDFields19a_UTF8.txt"
DEFAULT_OUT = "docs/mdf/build/master.json"

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


def parse_mdf_text(text: str, source_path: str) -> dict:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert the MDF 1.9a Toolbox field reference to a JSON intermediate representation."
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE, help=f"source .txt file (default: {DEFAULT_SOURCE})")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"output JSON path (default: {DEFAULT_OUT})")
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

    document = parse_mdf_text(text, args.source)
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

    summary = summarize(document, args.out)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
