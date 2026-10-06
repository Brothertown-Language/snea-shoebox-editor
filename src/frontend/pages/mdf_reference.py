# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""MDF Reference — in-app browser for the MDF 1.9a lexical-fields reference.

Renders all keyed topics from ``docs/mdf/build/master.json`` (schema
``snea-mdf-master/1``) with the source's own navigation model: the home/TOC
entry (``\\key aa``), the 17 chapter-topic groups in the home TOC order with
``\\shd2`` subsections nested, then the terminal "Field Marker Reference"
section grouping the marker-definition topics (Record Marker / Basic Fields /
Reserved Fields / Optional Fields / Discontinued, alphabetical by key within
each group) — the same semantic regrouping the PDF and HTML renderers
implement. The
detail pane preserves the source content; ``\\ftx``/``\\fxv`` formatting
examples render as code blocks; ``\\cf`` cross-references navigate in-app
and render green — the source's own stated convention, mirrored by the PDF
and HTML editions. The page owns the full window: the global sidebar
navigation is hidden and the MDF browser column is the single left rail,
with the standard back-to-main affordance at its top.

Layout (2026-10-06 directive): the browser rail and the detail pane form a
fixed-height split — each pane scrolls independently, a drag handle
resizes the rail (persisted in sessionStorage), a «/» control hides/shows
the rail (persisted), and every navigation (topic click, cf
cross-reference, ``?marker=`` deep link, unknown-key fallback) lands the
detail pane at its own top while the rail keeps its scroll position. The
behavior is implemented by a controller script re-injected on every rerun
(see ``_SPLIT_CONTROLLER_TEMPLATE``); without JavaScript the page
degrades to the plain whole-page two-column layout, fully functional.
Per the 2026-10-06 change control, cf blocks that are marker+gloss lookup
pairs render as a per-pair list — one row per pair, the source's own marker
token as the deep-link affordance and its gloss beside it, with in-gloss
marker mentions as live deep links (the 2026-10-06 paren-depth rule keeps
cross-referenced markers inside the gloss they annotate) — with strictly
consecutive glossed cf blocks coalesced into one list (the Introduction's
shd4 groups); bare-target cf blocks keep the caption + button grid.

Deep-linking: ``?marker=<topic-key>`` selects a topic; an unknown key falls
back to the home entry with a visible notice.

Unicode-first: any future filtering stays plain case-insensitive substring
matching on raw text (``str.lower()``) — no normalization, no stripping; the
source's accented content (á, ñ, é) must match losslessly (R-10).
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import quote

# Paths are resolved from this file's location (never Path.cwd()), mirroring
# src/database/connection.py's repo-root resolution.
_MASTER_REL = Path("docs") / "mdf" / "build" / "master.json"
_PDF_REL = Path("docs") / "mdf" / "build" / "mdf-lexical-fields-1.9a.pdf"
PDF_FILENAME = "mdf-lexical-fields-1.9a.pdf"
_FALLBACK_HOME_KEY = "aa"

# All ASCII punctuation CommonMark can treat specially; backslash-escaping it
# renders source content literally (marker mentions like ``\\ge`` and attribute
# lines like ``<Optional>`` stay verbatim instead of becoming markup).
_MD_PUNCT_RE = re.compile(r"([\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7E])")
# ``\\marker`` + exactly one separator whitespace; the remainder is the raw
# content byte-for-byte (presentation stripping belongs to renderers).
_MARKER_LINE_RE = re.compile(r"^\\(?P<tok>\S+)(?P<sep>\s)(?P<rest>.*)$", re.DOTALL)
# Maximum \\cf target buttons per row in the detail pane.
_CF_ROW_WIDTH = 6

# The terminal reference section's group apparatus — mirrors
# REFERENCE_GROUP_ORDER/REFERENCE_GROUP_TITLES/REFERENCE_CHAPTER_TITLE in
# scripts/convert_mdf_master.py so the in-app browser, PDF, and HTML all
# present the same semantic regrouping.
REFERENCE_GROUP_ORDER = ("record", "basic", "reserved", "optional", "discontinued")
REFERENCE_GROUP_TITLES = {
    "record": "Record Marker",
    "basic": "Basic Fields",
    "reserved": "Reserved Fields",
    "optional": "Optional Fields",
    "discontinued": "Discontinued",
}
REFERENCE_SECTION_TITLE = "Field Marker Reference"


def is_reference_entry(topic: dict, home_key: str | None) -> bool:
    """A single-marker definition topic: not the home entry, not a chapter
    topic, and a ``\\key`` naming exactly one marker (no internal whitespace).
    The multi-key "Old verb paradigm markers" stub is excluded here —
    placement_chapter rides it under Old_and_Changed_Markers per its own
    ``\\cf``."""
    return not topic["is_chapter"] and topic["key"] != home_key and " " not in topic["key"].strip()


def reference_group(topic: dict) -> str:
    """Deterministic reference group from the topic's own parsed data: ``\\lx``
    is the record marker (the SF catalog's own "RECORD MARKER" section);
    otherwise the ``\\typ`` block value (<Basic>/<Reserved>/<Optional>); a
    single-marker topic with no ``\\typ`` block is ``\\xg``, discontinued by
    its own heading wording."""
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
    chapter; a multi-key topic instead follows its own ``\\cf`` when that names
    a chapter topic (the source's placement for the numeric stub: "See the
    topic Old_and_Changed_Markers")."""
    if " " in topic["key"].strip():
        for block in topic["blocks"]:
            if block["marker"] == "cf":
                for target in block.get("targets", []):
                    if target in chapter_keys:
                        return target
    return topic["chapter"]


def browser_structure(topics: list[dict], chapter_keys: list[str], home_key: str | None) -> dict:
    """The browser's semantic structure — mirrors book_structure() in
    scripts/convert_mdf_master.py exactly, derived entirely from the parsed
    topics: the discussion chapters in home-TOC (chapter_keys) order, each
    followed by its non-reference member topics in document order; then the
    terminal reference groups with their single-marker entries alphabetical by
    key. Anything the grouping leaves unplaced keeps document order in
    "residual" (empty for the 1.9a source), so no topic is dropped and none is
    duplicated."""
    chapters: list[tuple[str, list[dict]]] = []
    home = next((topic for topic in topics if topic["key"] == home_key), None)
    placed: set[int] = {id(home)} if home is not None else set()
    for chapter_key in chapter_keys:
        if not any(topic["key"] == chapter_key for topic in topics):
            continue
        placed.add(id(next(topic for topic in topics if topic["key"] == chapter_key)))
        members = [
            topic
            for topic in topics
            if not topic["is_chapter"]
            and topic["key"] != home_key
            and not is_reference_entry(topic, home_key)
            and placement_chapter(topic, chapter_keys) == chapter_key
        ]
        placed.update(id(member) for member in members)
        chapters.append((chapter_key, members))

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
    return {"chapters": chapters, "residual": residual, "reference": groups}


def project_root() -> Path:
    """Repository root, resolved from this file's location.

    This page lives three levels below the repo root (src/frontend/pages/),
    so the root is parents[3] — the same resolution as
    src/database/connection.py's parents[2], which sits one level shallower.
    """
    return Path(__file__).resolve().parents[3]


def load_master(root: Path | None = None) -> dict | None:
    """Load the committed MDF intermediate representation.

    Returns None when the file is missing or unreadable — the page shows an
    actionable error instead of crashing (missing-artifact edge case). The
    failure is logged server-side so a broken checkout is diagnosable.
    """
    path = (root or project_root()) / _MASTER_REL
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        from src.logging_config import get_logger

        get_logger("snea.mdf_reference").warning(
            "master.json failed to load from %s", path, exc_info=True
        )
        return None


def load_pdf_bytes(root: Path | None = None) -> bytes | None:
    """Load the committed PDF deliverable's bytes; None when not built yet."""
    path = (root or project_root()) / _PDF_REL
    try:
        return path.read_bytes()
    except OSError:
        return None


def resolve_selection(marker_param, topics_by_key: dict, home_key: str) -> tuple[str, str | None]:
    """Resolve the ``?marker=`` deep link to a topic key.

    Returns (selected_key, notice): an unknown key falls back to the home
    entry with a notice string naming the rejected key (never raises, never
    blanks the pane).
    """
    if marker_param is None:
        return home_key, None
    if marker_param in topics_by_key:
        return marker_param, None
    return home_key, marker_param


def strip_marker(text: str) -> str:
    """Drop the line-initial ``\\marker`` token plus one separator whitespace.

    The remainder is preserved byte-for-byte; a marker line with no content
    yields an empty string.
    """
    match = _MARKER_LINE_RE.match(text)
    if match is None:
        return ""
    return match.group("rest")


def md_escape(text: str) -> str:
    """Backslash-escape every ASCII punctuation character for markdown.

    Renders the source text literally — no markup interpretation, no
    normalization, no character rewriting.
    """
    return _MD_PUNCT_RE.sub(r"\\\1", text)


def topic_search_text(topic: dict) -> str:
    """The raw text a filter query matches against: key, heading, preamble,
    and every block's raw content — nothing normalized, nothing stripped."""
    parts = [topic["key"], topic.get("heading") or ""]
    parts.extend(topic.get("preamble") or [])
    parts.extend(block.get("text", "") for block in topic.get("blocks", []))
    return "\n".join(parts)


def filter_topics(topics: list[dict], query: str) -> list[dict]:
    """Case-insensitive, Unicode-preserving substring match over keys and
    definition text (R-10).

    Plain ``str.lower()`` substring only — no unicode normalization, no
    stripping: the source's accented content (á, ñ, é) matches losslessly,
    and a decomposed query does not silently match precomposed text. Ranked
    full-text search is out of scope (deferred to #1417).
    """
    needle = (query or "").lower()
    if not needle:
        return list(topics)
    return [
        topic
        for topic in topics
        if needle in topic["key"].lower() or needle in topic_search_text(topic).lower()
    ]


def topic_display_heading(topic: dict) -> str:
    """Heading shown for a topic; falls back to the raw key when the source
    provides no ``\\shd`` heading (e.g. the References bibliography topic)."""
    heading = topic.get("heading")
    if heading:
        return heading
    return topic["key"]


def collect_cf_targets(master: dict) -> list[str]:
    """Every cross-reference target named by the source's ``\\cf`` fields,
    in source order (repeats preserved — 297 \\cf fields name 297+ targets)."""
    targets: list[str] = []
    for topic in master.get("topics", []):
        for block in topic.get("blocks", []):
            if block.get("marker") == "cf":
                targets.extend(block.get("targets") or [])
    return targets


def split_cf_targets(targets: list[str], known_keys: set) -> tuple[list[str], list[str]]:
    """Split \\cf targets into (resolved, missing) for navigation rendering.

    Missing targets are flagged here so the page can render a visible
    placeholder instead of a dead link (all 104 distinct targets resolve in
    the verified source; this guards future source revisions).
    """
    resolved = [t for t in targets if t in known_keys]
    missing = [t for t in targets if t not in known_keys]
    return resolved, missing


def pair_is_glossed(pair: dict) -> bool:
    """Mirror of the renderer predicate in scripts/convert_mdf_master.py: a
    lookup pair is glossed iff its gloss carries alphanumeric content — the
    parser never stores punctuation-only or connective-position fragments as
    gloss (they are list structure between pairs)."""
    return any(ch.isalnum() for ch in pair.get("gloss", ""))


def cf_block_glossed(block: dict) -> bool:
    """A cf block renders as a per-pair list iff ≥1 of its pairs is glossed
    (2026-10-06 change control); bare target lists (prose connectives like
    ``\\xe, \\xn, and \\xr``) keep the existing caption + button grid."""
    return any(pair_is_glossed(pair) for pair in block.get("pairs") or [])


def _ws_runs(text: str) -> list[tuple[bool, str]]:
    """Mirror of split_ws_runs() in scripts/convert_mdf_master.py: a plain
    character scan yields (is_whitespace, chunk) pairs covering the string
    exactly, so individual tokens can be rewritten while every other character
    (whitespace runs included) passes through verbatim."""
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


def pair_gloss_markdown(gloss: str, topics_by_key: dict) -> str:
    """A pair gloss with its own marker mentions as live deep links (2026-10-06
    paren-depth change control).

    Mirror of gloss_segments() in scripts/convert_mdf_master.py: each
    whitespace-delimited token whose candidate — leading backslash stripped,
    trailing ``*.,;:`` stripped, the same normalization the targets logic uses
    — is a known topic key (exact lookup against the rendered topics) renders
    as a markdown link through the page's existing ``?marker=`` deep-link
    mechanism; every other character (text and whitespace runs alike) passes
    through escaped-but-verbatim. The paren-depth pair extraction keeps
    cross-referenced markers inside the gloss they annotate, so a resolving
    token in a gloss is exactly such a mention.
    """
    parts: list[str] = []
    for is_space, chunk in _ws_runs(gloss):
        if is_space:
            parts.append(chunk)
            continue
        candidate = chunk[1:] if chunk.startswith("\\") else chunk
        while candidate and candidate[-1] in "*.,;:":
            candidate = candidate[:-1]
        if candidate in topics_by_key:
            parts.append(f"[{md_escape(chunk)}](?marker={quote(candidate)})")
        else:
            parts.append(md_escape(chunk))
    return "".join(parts)


def render_cf_pair_rows(
    st, run: list[dict], selected: str, first_block_index: int, navigate_to, topics_by_key: dict
) -> None:
    """One row per lookup pair (2026-10-06 change control): the source's own
    marker token as a deep-link affordance to the target topic, its gloss
    beside it with in-gloss marker mentions as live deep links — the in-app
    mirror of the PDF/HTML description-list rendering. Pair targets resolve by
    construction (the parser starts a pair only on a target-set hit), so no
    missing-target placeholder is needed."""
    for run_offset, block in enumerate(run):
        block_index = first_block_index + run_offset
        for pair_pos, pair in enumerate(block.get("pairs") or []):
            cols = st.columns([1, 3], gap="small")
            if cols[0].button(
                pair.get("token") or pair["target"],
                key=f"mdf-cf-pair-{selected}-{block_index}-{pair_pos}",
                help=f"Open the {pair['target']} reference entry",
                use_container_width=True,
            ):
                navigate_to(pair["target"])
            gloss = pair.get("gloss") or ""
            if gloss:
                cols[1].markdown(pair_gloss_markdown(gloss, topics_by_key))


def _render_browser_tree(st, topics, topics_by_key, chapter_keys, selected, navigate_to, home_key):
    """Render the unfiltered browser: home entry; the 17 chapter groups in
    home TOC order with ``\\shd2`` subsections nested and only their
    non-reference member topics (the multi-key verb-paradigm stub rides its
    source-directed chapter); then the terminal Field Marker Reference section
    with its five groups of single-marker entries."""
    # Home/TOC entry — the source's own navigation model starts here. The
    # button is labeled "Home (aa)" for users (the bare key is meaningless to
    # them); the source key stays in parentheses for traceability, and the
    # detail pane's heading remains the source's own \shd text.
    if st.button(
        f"Home ({home_key})",
        key=f"mdf-topic-{home_key}",
        use_container_width=True,
        type="primary" if selected == home_key else "secondary",
    ):
        navigate_to(home_key)
    structure = browser_structure(topics, chapter_keys, home_key)
    # 17 chapter-topic groups, in the home TOC order.
    for chapter_key, members in structure["chapters"]:
        chapter_topic = topics_by_key[chapter_key]
        st.markdown(f"### {md_escape(topic_display_heading(chapter_topic))}")
        if st.button(
            chapter_key,
            key=f"mdf-topic-{chapter_key}",
            use_container_width=True,
            type="primary" if selected == chapter_key else "secondary",
        ):
            navigate_to(chapter_key)
        # \\shd2 subsections nested inside the chapter's own body.
        for i, block in enumerate(chapter_topic["blocks"]):
            if block["marker"] != "shd2":
                continue
            label = "▸ " + strip_marker(block["text"]).strip()
            if st.button(
                label,
                key=f"mdf-shd2-{chapter_key}-{i}",
                use_container_width=True,
                type="secondary",
            ):
                navigate_to(chapter_key)
        # Member topics belonging to this chapter, in source order.
        for member in members:
            if st.button(
                member["key"],
                key=f"mdf-topic-{member['key']}",
                use_container_width=True,
                type="primary" if selected == member["key"] else "secondary",
            ):
                navigate_to(member["key"])
    # Anything the grouping leaves unplaced keeps document order (empty for
    # the 1.9a source) — no topic is dropped from the browser.
    for topic in structure["residual"]:
        if st.button(
            topic["key"],
            key=f"mdf-topic-{topic['key']}",
            use_container_width=True,
            type="primary" if selected == topic["key"] else "secondary",
        ):
            navigate_to(topic["key"])
    # Terminal reference section: the marker-definition topics grouped
    # record/basic/reserved/optional/discontinued, alphabetical by key.
    if structure["reference"]:
        st.markdown(f"### {md_escape(REFERENCE_SECTION_TITLE)}")
        for group, entries in structure["reference"].items():
            st.markdown(f"#### {md_escape(REFERENCE_GROUP_TITLES[group])}")
            for entry in entries:
                if st.button(
                    entry["key"],
                    key=f"mdf-topic-{entry['key']}",
                    use_container_width=True,
                    type="primary" if selected == entry["key"] else "secondary",
                ):
                    navigate_to(entry["key"])


# ── Split-pane controller (2026-10-06 layout directive) ─────────────────
#
# Streamlit reruns rebuild the page DOM, so the split-pane behavior cannot be
# a one-time setup: the controller script is re-injected on every rerun (the
# per-run nonce in the body changes the sanitized string, which re-triggers
# the frontend's html renderer effect) and re-applies everything idempotently
# from sessionStorage. It runs in the app document itself — Streamlit 1.54's
# st.html is not iframed; scripts execute only with
# unsafe_allow_javascript=True (verified live: without the flag they are
# dropped, and a components.html iframe reaches window.parent.document only
# same-origin — the non-iframed path is the simpler, equivalent surface).
#
# Behaviors, all graceful-degrading (no JavaScript → the plain whole-page
# two-column layout, fully functional, just not resizable):
#   1. The two-column block is pinned to the viewport height; each column
#      becomes its own scroll container (split-pane scrolling).
#   2. A drag handle between the panes resizes the rail (persisted).
#   3. A «/» control hides/shows the rail (persisted).
#   4. Any navigation — a ?marker= query-param change (deep links, unknown
#      keys, in-app topic/cf clicks whose URL update lands asynchronously
#      after the rerun) or a detail-heading change (the same rerun the new
#      topic renders in) — scrolls the DETAIL pane to its own top, while the
#      rail's scroll position is saved to and restored from sessionStorage.
_SPLIT_CONTROLLER_TEMPLATE = """
<div id="mdf-split-anchor"></div>
<script>
/* mdf-split nonce @@NONCE@@ */
(function () {
    'use strict';
    var K = {
        width: 'mdfSplit.railWidth',
        collapsed: 'mdfSplit.railCollapsed',
        lastMarker: 'mdfSplit.lastMarker',
        lastHeading: 'mdfSplit.lastHeading',
        railScroll: 'mdfSplit.railScroll'
    };
    function ssGet(k) {
        try { return window.sessionStorage.getItem(k); } catch (e) { return null; }
    }
    function ssSet(k, v) {
        try { window.sessionStorage.setItem(k, String(v)); } catch (e) {}
    }
    function markerParam() {
        try {
            var m = new URLSearchParams(window.location.search).get('marker');
            return m === null ? '' : m;
        } catch (e) { return ''; }
    }
    function detailPane() {
        return document.querySelector('[data-mdsplit-detail]');
    }
    function forceTop(el) {
        // Navigation lands the pane at its top; the settle window covers
        // the rest of Streamlit's post-rerun content streaming.
        var n = 0;
        var tick = function () {
            if (el.scrollTop !== 0) { el.scrollTop = 0; }
            if (n++ < 9) { window.setTimeout(tick, 100); }
        };
        el.scrollTop = 0;
        window.setTimeout(tick, 100);
    }
    function checkMarker() {
        var cur = markerParam();
        var last = ssGet(K.lastMarker);
        if (last === cur) { return; }
        ssSet(K.lastMarker, cur);
        var detail = detailPane();
        if (detail) { forceTop(detail); }
    }
    function checkHeading() {
        var h2 = document.querySelector('[data-mdsplit-detail] h2');
        var cur = h2 ? h2.textContent.trim() : '';
        if (!cur) { return; }
        var last = ssGet(K.lastHeading);
        ssSet(K.lastHeading, cur);
        if (last === null || last === cur) { return; }
        var detail = detailPane();
        if (detail) { forceTop(detail); }
    }
    function findSplit() {
        // The page's own two-column block: the only horizontal block whose
        // wrapper chain is layoutWrapper > verticalBlock > block-container
        // (cf rows inside the detail pane nest far deeper).
        var blocks = document.querySelectorAll('[data-testid="stHorizontalBlock"]');
        for (var i = 0; i < blocks.length; i++) {
            var hb = blocks[i];
            var cols = [];
            for (var j = 0; j < hb.children.length; j++) {
                var ch = hb.children[j];
                if (ch.getAttribute && ch.getAttribute('data-testid') === 'stColumn') {
                    cols.push(ch);
                }
            }
            if (cols.length !== 2) { continue; }
            var wrap = hb.parentElement;
            if (!wrap || wrap.getAttribute('data-testid') !== 'stLayoutWrapper') { continue; }
            var vb = wrap.parentElement;
            if (!vb || vb.getAttribute('data-testid') !== 'stVerticalBlock') { continue; }
            var bc = vb.parentElement;
            if (!bc) { continue; }
            if (bc.getAttribute('data-testid') !== 'stMainBlockContainer' &&
                !(bc.classList && bc.classList.contains('block-container'))) { continue; }
            return { hb: hb, rail: cols[0], detail: cols[1], handle: null };
        }
        return null;
    }
    function clampWidth(w) {
        return Math.min(Math.max(w, 220), Math.round(window.innerWidth * 0.7));
    }
    function applyWidth(state) {
        var saved = parseInt(ssGet(K.width) || '', 10);
        if (!saved) {
            saved = Math.round(state.rail.getBoundingClientRect().width);
            ssSet(K.width, saved);
        }
        saved = clampWidth(saved);
        state.rail.style.flex = '0 0 ' + saved + 'px';
        state.rail.style.minWidth = '0';
        state.detail.style.flex = '1 1 0%';
        state.detail.style.minWidth = '0';
    }
    function fitHeight(state) {
        var hb = state.hb;
        // The layout wrapper is a column flex container and this block is
        // its flex item: without flex:none the item grows to its content
        // height and the inline height never takes effect.
        hb.style.flex = '0 0 auto';
        hb.style.minHeight = '0';
        var top = hb.getBoundingClientRect().top +
            (window.scrollY || window.pageYOffset || 0);
        var h = Math.max(480, window.innerHeight - top - 4);
        hb.style.height = h + 'px';
        // If anything still overflows the viewport (theme paddings and
        // margins), shrink the split by the measured overflow instead of
        // hard-coding offsets.
        var scroller = document.querySelector('section.stMain');
        if (scroller) {
            var over = scroller.scrollHeight - scroller.clientHeight;
            if (over > 0 && h - over >= 480) { hb.style.height = (h - over) + 'px'; }
        }
        var docOver = document.documentElement.scrollHeight - window.innerHeight;
        if (docOver > 0 && h - docOver >= 480) { hb.style.height = (h - docOver) + 'px'; }
    }
    function positionHandle(state) {
        var handle = state.handle;
        if (!handle || ssGet(K.collapsed) === '1') { return; }
        var rr = state.rail.getBoundingClientRect();
        var hr = state.hb.getBoundingClientRect();
        handle.style.left = Math.round(rr.right - hr.left - handle.offsetWidth / 2) + 'px';
    }
    function startDrag(ev, state) {
        if (ev.button !== 0) { return; }
        var startX = ev.clientX;
        var startW = state.rail.getBoundingClientRect().width;
        state.hb.classList.add('mdf-dragging');
        document.body.style.userSelect = 'none';
        function onMove(e) {
            var w = clampWidth(startW + (e.clientX - startX));
            state.rail.style.flex = '0 0 ' + w + 'px';
            ssSet(K.width, w);
            positionHandle(state);
            e.preventDefault();
        }
        function onUp() {
            state.hb.classList.remove('mdf-dragging');
            document.body.style.userSelect = '';
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        }
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
        ev.preventDefault();
    }
    function applyCollapsed(state) {
        state.hb.classList.toggle('mdf-rail-collapsed', ssGet(K.collapsed) === '1');
    }
    function setCollapsed(state, collapsed) {
        ssSet(K.collapsed, collapsed ? '1' : '0');
        applyCollapsed(state);
        positionHandle(state);
    }
    function buildChrome(state) {
        var hb = state.hb;
        var rail = state.rail;
        var handle = hb.querySelector(':scope > .mdf-split-handle');
        if (!handle) {
            handle = document.createElement('div');
            handle.className = 'mdf-split-handle';
            handle.title = 'Drag to resize the browser panel';
            handle.addEventListener('mousedown', function (ev) { startDrag(ev, state); });
            hb.appendChild(handle);
        }
        state.handle = handle;
        var expand = hb.querySelector(':scope > .mdf-split-expand');
        if (!expand) {
            expand = document.createElement('button');
            expand.type = 'button';
            expand.className = 'mdf-split-expand';
            expand.title = 'Show browser panel';
            expand.setAttribute('aria-label', 'Show browser panel');
            expand.textContent = '\\u00BB';
            expand.addEventListener('click', function () { setCollapsed(state, false); });
            hb.appendChild(expand);
        }
        var strip = rail.querySelector(':scope > .mdf-rail-strip');
        if (!strip) {
            strip = document.createElement('div');
            strip.className = 'mdf-rail-strip';
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'mdf-split-toggle';
            btn.title = 'Hide browser panel';
            btn.setAttribute('aria-label', 'Hide browser panel');
            btn.textContent = '\\u00AB';
            btn.addEventListener('click', function () { setCollapsed(state, true); });
            strip.appendChild(btn);
            rail.insertBefore(strip, rail.firstChild);
        }
        if (!rail.__mdfScrollHooked) {
            rail.__mdfScrollHooked = true;
            var pending = null;
            rail.addEventListener('scroll', function () {
                if (pending) { return; }
                pending = window.setTimeout(function () {
                    pending = null;
                    ssSet(K.railScroll, Math.round(rail.scrollTop));
                }, 120);
            }, { passive: true });
        }
    }
    function restoreRailScroll(rail) {
        var saved = parseInt(ssGet(K.railScroll) || '0', 10);
        if (!(saved > 40)) { return; }
        var n = 0;
        var tick = function () {
            if (rail.scrollTop === 0) { rail.scrollTop = saved; }
            if (n++ < 7) { window.setTimeout(tick, 120); }
        };
        if (rail.scrollTop === 0) { rail.scrollTop = saved; }
        window.setTimeout(tick, 120);
    }
    // One-time installs (guarded): they survive reruns because they hang
    // off window, not off the re-rendered DOM.
    if (!window.__mdfSplitLive) {
        window.__mdfSplitLive = true;
        // st.query_params pushes the URL asynchronously AFTER a navigation
        // rerun renders, so a poll — not just the per-rerun inline check —
        // is what reliably sees ?marker= change (deep links included).
        window.setInterval(function () { checkMarker(); }, 200);
        window.addEventListener('resize', function () {
            var api = window.__mdfSplitApi;
            if (api) { api.refresh(); }
        });
    }
    var state = findSplit();
    if (state) {
        state.hb.setAttribute('data-mdsplit', '1');
        state.rail.setAttribute('data-mdsplit-rail', '1');
        state.detail.setAttribute('data-mdsplit-detail', '1');
        state.rail.style.overflowY = 'auto';
        state.rail.style.overflowX = 'hidden';
        state.rail.style.height = '100%';
        state.detail.style.overflowY = 'auto';
        state.detail.style.overflowX = 'hidden';
        state.detail.style.height = '100%';
        applyWidth(state);
        buildChrome(state);
        applyCollapsed(state);
        fitHeight(state);
        positionHandle(state);
        restoreRailScroll(state.rail);
        checkHeading();
        checkMarker();
        window.__mdfSplitApi = {
            refresh: function () {
                applyWidth(state);
                fitHeight(state);
                positionHandle(state);
            }
        };
        // Fonts/images settle right after attach; re-fit briefly.
        window.setTimeout(function () { fitHeight(state); positionHandle(state); }, 250);
        window.setTimeout(function () { fitHeight(state); positionHandle(state); }, 900);
    }
})();
</script>
"""


def _render_split_controller() -> None:
    """Inject the split-pane controller script (see the template's rationale).

    The nonce comment inside the body changes on every rerun, which makes the
    frontend's html renderer re-run its effect (its memo key is the sanitized
    body string) and therefore re-execute the script after Streamlit rebuilt
    the page DOM.
    """
    import streamlit as st

    body = _SPLIT_CONTROLLER_TEMPLATE.replace("@@NONCE@@", str(time.time_ns()))
    st.html(body, unsafe_allow_javascript=True)


def mdf_reference():
    """Render the MDF Reference page (chapter-grouped browser + detail pane)."""
    import streamlit as st

    from src.frontend.ui_utils import (
        apply_standard_layout_css,
        hide_sidebar_nav,
        render_back_to_main_button,
    )

    # The MDF browser column below is this view's single left rail (the
    # Records pattern): the global navigation sidebar is hidden and the
    # standard back-to-main affordance rides at the top of the rail.
    hide_sidebar_nav()
    apply_standard_layout_css()
    st.html(
        """
        <style>
        /* Drop the dead band above the detail pane heading: the fixed
           6rem block-container top padding pushed the first heading
           ~140px down the pane. */
        .block-container {
            padding-top: 1rem;
        }
        /* With the nav hidden the global sidebar holds nothing — but
           Streamlit still expands it as a blank 300px rail. This page's
           browser column is the single left rail, so the empty container
           goes away entirely. */
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Cross-references render green — the source's own stated
           convention, mirrored by the PDF/HTML editions (--cf-green
           #067d06). Every enabled button in the detail column is a
           \\cf navigation affordance; the gloss links and the cf caption
           carry their own hooks. Disabled missing-target placeholders
           keep their muted error look. */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:not([disabled]) p,
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:not([disabled]),
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) a[href*="marker="],
        .mdf-cf-caption {
            color: #067d06 !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:not([disabled]) {
            border-color: #067d06;
        }
        /* The selected-topic chip uses the app's emphasis orange (the
           Records suggestion/status accent) — the theme's coral primary
           reads as an error state. */
        button[kind="primary"],
        button[kind="primary"]:hover {
            background-color: #ffa500;
            border-color: #ffa500;
        }
        button[kind="primary"] p {
            color: #313338 !important;
        }
        /* ── Split-pane layout (2026-10-06 layout directive) ─────────────
           The page's two-column block is pinned to the viewport by the
           controller script injected at the bottom of the page: each pane
           scrolls independently, a drag handle between the panes resizes
           the browser rail (persisted in sessionStorage), and a «/» control
           hides/shows the rail (persisted). Without JavaScript the page
           degrades to the unsplit whole-page layout — fully functional,
           just not resizable. */
        .block-container {
            padding-bottom: 0;
        }
        /* The controller element itself is pure script — its layout slot
           goes away entirely (script still runs: hiding does not unmount). */
        div[data-testid="stElementContainer"]:has(> #mdf-split-anchor) {
            display: none;
        }
        [data-mdsplit] {
            position: relative;
            overflow: hidden;
        }
        .mdf-split-handle {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 12px;
            cursor: col-resize;
            z-index: 40;
            touch-action: none;
        }
        .mdf-split-handle::after {
            content: "";
            position: absolute;
            top: 4px;
            bottom: 4px;
            left: 5px;
            width: 2px;
            border-radius: 1px;
            background: rgba(128, 128, 128, 0.35);
        }
        .mdf-split-handle:hover::after,
        [data-mdsplit].mdf-dragging .mdf-split-handle::after {
            background: #ffa500;
        }
        /* Rail-top control strip: the « collapse control rides the rail's
            top edge (sticky — stays visible while the rail scrolls),
            mirroring the app sidebar's collapse affordance. */
        .mdf-rail-strip {
            position: sticky;
            top: 0;
            z-index: 30;
            display: flex;
            justify-content: flex-end;
            padding: 2px 4px 2px 0;
            pointer-events: none;
            background: var(--background-color, transparent);
        }
        .mdf-split-toggle,
        .mdf-split-expand {
            pointer-events: auto;
            width: 24px;
            height: 24px;
            padding: 0;
            border: 1px solid rgba(128, 128, 128, 0.45);
            border-radius: 6px;
            background: transparent;
            color: inherit;
            font-size: 14px;
            line-height: 1;
            cursor: pointer;
        }
        .mdf-split-toggle:hover,
        .mdf-split-expand:hover {
            border-color: #ffa500;
            color: #ffa500;
        }
        /* Collapsed state: the » expand tab floats at the split's left
           edge; the rail and the handle are removed from the flow. */
        .mdf-split-expand {
            display: none;
            position: absolute;
            top: 6px;
            left: 4px;
            z-index: 40;
        }
        [data-mdsplit].mdf-rail-collapsed .mdf-split-expand {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        [data-mdsplit].mdf-rail-collapsed > [data-mdsplit-rail] {
            display: none !important;
        }
        [data-mdsplit].mdf-rail-collapsed > .mdf-split-handle {
            display: none !important;
        }
        </style>
        """
    )

    master = load_master()
    if (
        not isinstance(master, dict)
        or not isinstance(master.get("topics"), list)
        or not master["topics"]
        or not isinstance(master.get("chapter_keys"), list)
    ):
        st.error("The MDF reference data (docs/mdf/build/master.json) is missing or unreadable.")
        st.info("Regenerate it with: uv run python scripts/convert_mdf_master.py — then reload this page.")
        return

    topics: list[dict] = master["topics"]
    topics_by_key: dict[str, dict] = {t["key"]: t for t in topics}
    chapter_keys: list[str] = list(master["chapter_keys"])
    home_key = master.get("home_key") or _FALLBACK_HOME_KEY
    if home_key not in topics_by_key:
        home_key = chapter_keys[0] if chapter_keys else topics[0]["key"]

    marker_param = st.query_params["marker"] if "marker" in st.query_params else None
    selected, unknown_notice = resolve_selection(marker_param, topics_by_key, home_key)

    def _navigate_to(key: str) -> None:
        st.query_params["marker"] = key
        st.rerun()

    st.title("MDF Reference")
    left, main = st.columns([1, 2], gap="medium")

    with left:
        render_back_to_main_button()
        st.caption(f"{len(topics)} topics · MDF 1.9a field reference")
        # R-13/R-14: the committed PDF deliverable is offered from the page's
        # left browser column, served under its content-accurate name.
        pdf_bytes = load_pdf_bytes()
        if pdf_bytes is None:
            st.warning(
                "The PDF deliverable (docs/mdf/build/mdf-lexical-fields-1.9a.pdf) is not built yet. "
                "Generate it with: bash scripts/build_mdf_docs.sh"
            )
        else:
            st.download_button(
                "Download the MDF reference (PDF)",
                data=pdf_bytes,
                file_name=PDF_FILENAME,
                mime="application/pdf",
                key="mdf_pdf_download",
                use_container_width=True,
            )
        query = st.text_input(
            "Filter topics (substring, case-insensitive)",
            key="mdf_filter",
        )
        query = (query or "").strip()
        if query:
            matches = filter_topics(topics, query)
            st.caption(f"{len(matches)} matching topics")
            if not matches:
                st.info("No topics match your filter. Clear the filter to see the full chapter list.")
            for match in matches:
                if st.button(
                    match["key"],
                    key=f"mdf-topic-{match['key']}",
                    use_container_width=True,
                    type="primary" if selected == match["key"] else "secondary",
                ):
                    _navigate_to(match["key"])
        else:
            _render_browser_tree(st, topics, topics_by_key, chapter_keys, selected, _navigate_to, home_key)

    with main:
        topic = topics_by_key[selected]
        if unknown_notice:
            st.warning(f"No reference topic '{unknown_notice}' — showing the MDF home entry instead.")
        st.header(md_escape(topic_display_heading(topic)))
        # 2026-10-06 directive: visible ``\key`` annotations are dropped — the
        # heading and structure carry the topic's identity (the former
        # "key <key> · source line N" caption showed only parser provenance,
        # none of which the PDF/HTML surfaces render).
        blocks = topic["blocks"]
        block_index = 0
        while block_index < len(blocks):
            block = blocks[block_index]
            marker = block["marker"]
            text = block["text"]
            if marker == "shd":
                block_index += 1
                continue  # the heading is rendered above
            if marker == "cf" and cf_block_glossed(block):
                # 2026-10-06 change control: strictly consecutive glossed cf
                # blocks coalesce into ONE per-pair list (the shd4 groups).
                run_end = block_index + 1
                while (
                    run_end < len(blocks)
                    and blocks[run_end]["marker"] == "cf"
                    and cf_block_glossed(blocks[run_end])
                ):
                    run_end += 1
                render_cf_pair_rows(
                    st, blocks[block_index:run_end], selected, block_index, _navigate_to, topics_by_key
                )
                block_index = run_end
                continue
            if marker in ("shd2", "shd3", "shd4"):
                level = {"shd2": "#### ", "shd3": "##### ", "shd4": "###### "}[marker]
                st.markdown(level + md_escape(strip_marker(text).strip()))
            elif marker in ("ftx", "fxv"):
                st.code(strip_marker(text), language=None)
            elif marker == "cf":
                # The classed span hooks the green cross-reference styling
                # (the source's own convention); unsafe_allow_html only lets
                # that one static wrapper tag through.
                st.caption(
                    '<span class="mdf-cf-caption">→ ' + md_escape(strip_marker(text)).strip() + "</span>",
                    unsafe_allow_html=True,
                )
                targets = block.get("targets") or []
                resolved, missing = split_cf_targets(targets, set(topics_by_key))
                for t in missing:
                    st.button(
                        f"⚠ {t} — topic not found",
                        key=f"mdf-cf-missing-{selected}-{block_index}-{t}",
                        disabled=True,
                        help="The source names this cross-reference target, but no such topic exists.",
                        use_container_width=True,
                    )
                for row_start in range(0, len(resolved), _CF_ROW_WIDTH):
                    row = resolved[row_start : row_start + _CF_ROW_WIDTH]
                    cols = st.columns(len(row))
                    for col, target in zip(cols, row, strict=True):
                        if col.button(
                            target,
                            key=f"mdf-cf-{selected}-{block_index}-{row_start}-{target}",
                            use_container_width=True,
                            help=f"Open the {target} reference entry",
                        ):
                            _navigate_to(target)
            elif marker == "typ":
                st.caption(md_escape(strip_marker(text)).strip())
            elif marker == "nt":
                st.caption("📝 " + md_escape(strip_marker(text)).strip())
            elif marker == "bib":
                st.caption("📚 " + md_escape(strip_marker(text)).strip())
            else:  # txt, nwt, and any continuation-bearing content marker
                st.markdown(md_escape(strip_marker(text)))
            block_index += 1

    # Injected AFTER both panes render, so the controller attaches to the
    # finished two-column DOM on every rerun (see _SPLIT_CONTROLLER_TEMPLATE).
    _render_split_controller()


if __name__ == "__main__":
    mdf_reference()
