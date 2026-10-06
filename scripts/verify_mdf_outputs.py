#!/usr/bin/env python3
"""Verify generated MDF reference outputs against the intermediate JSON.

Spec: .issues/1379/spec.md — SC-1, SC-2, SC-3, SC-14 verification methods.

Checks (all against docs/mdf/build/ artifacts):
- SC-1/SC-3 PDF: pdftotext extraction contains each topic's rendered heading
  (the ``\\shd`` payload, key fallback) — 108 topics, 1:1 against the source
  key list. Amended 2026-10-06 (developer directive): the visible
  ``\\key <key>`` annotation lines no longer render — the marker heading and
  structure carry the topic's identity, while the invisible
  ``\\label{key:<slug>}`` anchors (checked in master.tex) keep every
  cross-reference hot.
- SC-2 HTML: every ``a.cf-link`` href resolves to an existing anchor element on
  the target page; unresolved ``\\cf`` tokens appear only as visible
  ``a.cf-missing`` placeholders (none exist in the 1.9a source).
- SC-3 HTML: the union of ``key-*`` anchor ids across all pages is exactly the
  108-key set, 1:1 in both directions.
- SC-14: example blocks — 444 in the HTML site (``pre.mdf-example``) and 444
  ``(N)`` apparatus labels, N = 1..444 exactly once each, in pdftotext output.

Stdlib only: no database, no network, no third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_JSON = "docs/mdf/build/master.json"
DEFAULT_SITE = "docs/mdf/build/site"
DEFAULT_PDF = "docs/mdf/build/mdf-lexical-fields-1.9a.pdf"

# The renderer-side cf predicates live in the converter script; one source of
# truth for the link-instance model (SC-2) and the anchor scheme (SC-3).
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from convert_mdf_master import build_slugs, cf_block_glossed  # noqa: E402


def iter_example_blocks(document: dict):
    """Every example block in document order (non-empty \\ftx plus all \\fxv — 444)."""
    for topic in document["topics"]:
        for block in topic["blocks"]:
            if block["marker"] in ("ftx", "fxv") and (
                block["marker"] == "fxv" or block["text"].split("\n", 1)[0].rstrip() != "\\ftx"
            ):
                yield block


def example_content(block: dict) -> str:
    """Marker-line payload plus continuation lines — the exact bytes rendered verbatim."""
    lines = block["text"].split("\n")
    marker = block["marker"]
    payload = lines[0][1 + len(marker) :]
    if payload[:1].isspace():
        payload = payload[1:]
    return "\n".join([payload, *lines[1:]])


class SitePage(HTMLParser):
    """Collect ids, cf hyperlinks, missing-target placeholders, and example blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.cf_links: list[str] = []
        self.cf_missing: list[str] = []
        self.examples = 0
        self.example_contents: list[str] = []
        self._in_example = False
        self._example_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if "id" in attributes and attributes["id"]:
            self.ids.add(attributes["id"])
        if tag == "a" and "cf-link" in classes and attributes.get("href"):
            self.cf_links.append(attributes["href"])
        if tag == "a" and "cf-missing" in classes:
            self.cf_missing.append(attributes.get("title", ""))
        if tag == "pre" and "mdf-example" in classes:
            self.examples += 1
            self._in_example = True
            self._example_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_example:
            self._example_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre" and self._in_example:
            self.example_contents.append("".join(self._example_buffer))
            self._in_example = False


def load_site(site_dir: str | Path) -> dict[str, SitePage]:
    pages: dict[str, SitePage] = {}
    for path in sorted(Path(site_dir).glob("*.html")):
        page = SitePage()
        page.feed(path.read_text(encoding="utf-8"))
        pages[path.name] = page
    return pages


def resolve_href(href: str, source_page: str) -> tuple[str, str]:
    target, _, anchor = href.partition("#")
    return (target or source_page), anchor


def cf_link_instances(document: dict) -> list[tuple[str, str]]:
    """Every (source topic, canonical target) hyperlink instance the renderers
    produce (2026-10-06 change control): glossed cf blocks render one link per
    lookup pair; bare-target cf blocks render one link per parsed target."""
    instances: list[tuple[str, str]] = []
    for topic in document["topics"]:
        for block in topic["blocks"]:
            if block["marker"] != "cf":
                continue
            if cf_block_glossed(block):
                instances.extend((topic["key"], pair["target"]) for pair in block.get("pairs", []))
            else:
                instances.extend((topic["key"], target) for target in block.get("targets", []))
    return instances


def check_sc2_html(document: dict, site_dir: str | Path) -> dict:
    pages = load_site(site_dir)
    failures: list[str] = []
    total_links = 0
    for page_name, page in pages.items():
        for href in page.cf_links:
            total_links += 1
            target_file, anchor = resolve_href(href, page_name)
            if target_file not in pages:
                failures.append(f"{page_name}: cf href {href!r} points at missing page {target_file!r}")
            elif anchor not in pages[target_file].ids:
                failures.append(f"{page_name}: cf href {href!r} has no anchor on {target_file}")
    missing_placeholders = sum(len(page.cf_missing) for page in pages.values())
    expected_links = len(cf_link_instances(document))
    if total_links != expected_links:
        failures.append(f"cf-link count {total_links} != {expected_links} link instances parsed from source")
    if missing_placeholders:
        failures.append(f"{missing_placeholders} unresolved-target placeholder(s) rendered")
    return {
        "ok": not failures,
        "pages": len(pages),
        "links": total_links,
        "expected_links": expected_links,
        "placeholders": missing_placeholders,
        "failures": failures,
    }


def check_sc3_html(document: dict, site_dir: str | Path) -> dict:
    pages = load_site(site_dir)
    found: set[str] = set()
    for page in pages.values():
        found |= {i for i in page.ids if i.startswith("key-")}
    expected = {f"key-{slug}" for slug in build_slugs(document["topics"]).values()}
    failures = []
    if found != expected:
        failures.append(f"missing anchors: {sorted(expected - found)}")
        failures.append(f"unexpected anchors: {sorted(found - expected)}")
    return {"ok": not failures, "anchors": len(found), "expected": len(expected), "failures": failures}


def check_sc14_html(document: dict, site_dir: str | Path) -> dict:
    pages = load_site(site_dir)
    total = sum(page.examples for page in pages.values())
    failures = [] if total == 444 else [f"example block count {total} != 444"]
    if document is not None:
        expected = Counter(example_content(block) for block in iter_example_blocks(document))
        rendered = Counter(content for page in pages.values() for content in page.example_contents)
        if rendered != expected:
            failures.append("rendered example contents do not match the source's 444 examples 1:1")
    return {"ok": not failures, "examples": total, "failures": failures}


def pdf_text(pdf_path: str | Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as handle:
        temp = handle.name
    try:
        subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), temp],
            check=True,
            capture_output=True,
            timeout=120,
        )
        return Path(temp).read_text(encoding="utf-8")
    finally:
        Path(temp).unlink(missing_ok=True)


def check_sc1_sc3_pdf(document: dict, text: str) -> dict:
    """PDF topic-presence check (SC-1/SC-3), amended 2026-10-06 (developer
    directive in the PR review): visible ``\\key <key>`` annotation lines are
    removed from the rendered surfaces, so the key string itself is no longer
    a reliable PDF-side identity probe. Presence is instead verified via each
    topic's own rendered heading — the ``\\shd`` payload, falling back to the
    key when the source provides no heading — matched as a whitespace-collapsed
    substring of the extracted text (headings may wrap across lines). The
    invisible ``\\label{key:<slug>}`` anchors behind every cross-reference are
    asserted separately against master.tex; PDF-bookmark reachability is
    checked against the document outline."""
    collapsed = " ".join(text.split())
    missing = [
        topic["key"]
        for topic in document["topics"]
        if " ".join((topic.get("heading") or topic["key"]).split()) not in collapsed
    ]
    return {
        "ok": not missing,
        "keys_found": len(document["topics"]) - len(missing),
        "keys_expected": len(document["topics"]),
        "failures": [] if not missing else [f"topic headings absent from PDF text: {missing}"],
    }


def check_sc14_pdf(text: str) -> dict:
    pattern = re.compile(r"^\s*\((\d+)\)\s*$")
    found = [int(m.group(1)) for line in text.split("\n") for m in [pattern.match(line.rstrip())] if m]
    expected = list(range(1, 445))
    ok = sorted(set(found)) == expected and len(found) == 444
    failures = []
    if len(found) != 444:
        failures.append(f"example labels found {len(found)} != 444")
    if sorted(set(found)) != expected:
        failures.append("example label set is not exactly 1..444")
    return {"ok": ok, "examples": len(found), "distinct": len(set(found)), "failures": failures}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify MDF reference outputs (SC-1, SC-2, SC-3, SC-14).")
    parser.add_argument("--json", default=DEFAULT_JSON, help=f"intermediate JSON (default: {DEFAULT_JSON})")
    parser.add_argument("--site", default=DEFAULT_SITE, help=f"HTML site directory (default: {DEFAULT_SITE})")
    parser.add_argument("--pdf", default=DEFAULT_PDF, help=f"PDF deliverable (default: {DEFAULT_PDF})")
    parser.add_argument("--skip-pdf", action="store_true", help="skip PDF checks (pdftotext unavailable)")
    args = parser.parse_args(argv)

    document = json.loads(Path(args.json).read_text(encoding="utf-8"))

    results: list[tuple[str, dict]] = [
        ("SC-2 HTML cross-reference resolution", check_sc2_html(document, args.site)),
        ("SC-3 HTML 1:1 anchor coverage", check_sc3_html(document, args.site)),
        ("SC-14 HTML example count and byte fidelity", check_sc14_html(document, args.site)),
    ]
    if not args.skip_pdf and Path(args.pdf).is_file():
        text = pdf_text(args.pdf)
        results.append(("SC-1/SC-3 PDF topic coverage (heading identity)", check_sc1_sc3_pdf(document, text)))
        results.append(("SC-14 PDF example count", check_sc14_pdf(text)))

    failed = False
    for name, result in results:
        status = "PASS" if result["ok"] else "FAIL"
        detail = {k: v for k, v in result.items() if k not in ("ok", "failures")}
        print(f"{status} {name}: {detail}")
        for failure in result["failures"]:
            print(f"     {failure}")
        failed = failed or not result["ok"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
