# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""MDF Reference — in-app browser for the MDF 1.9a lexical-fields reference.

Renders all keyed topics from ``docs/mdf/build/master.json`` (schema
``snea-mdf-master/1``) with the source's own navigation model: the home/TOC
entry (``\\key aa``), the 17 chapter-topic groups in the home TOC order,
``\\shd2`` subsections nested, and marker entries inside each chapter. The
detail pane preserves the source content; ``\\ftx``/``\\fxv`` formatting
examples render as code blocks; ``\\cf`` cross-references navigate in-app.

Deep-linking: ``?marker=<topic-key>`` selects a topic; an unknown key falls
back to the home entry with a visible notice.

Unicode-first: any future filtering stays plain case-insensitive substring
matching on raw text (``str.lower()``) — no normalization, no stripping; the
source's accented content (á, ñ, é) must match losslessly (R-10).
"""

import json
import re
from pathlib import Path

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


def _render_browser_tree(st, topics, topics_by_key, chapter_keys, selected, navigate_to, home_key):
    """Render the unfiltered browser: home entry, 17 chapter groups in home
    TOC order with \\shd2 subsections nested, and member marker entries."""
    # Home/TOC entry — the source's own navigation model starts here.
    if st.button(
        home_key,
        key=f"mdf-topic-{home_key}",
        use_container_width=True,
        type="primary" if selected == home_key else "secondary",
    ):
        navigate_to(home_key)
    # 17 chapter-topic groups, in the home TOC order.
    for chapter_key in chapter_keys:
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
        # Marker entries belonging to this chapter, in source order.
        members = [t for t in topics if t.get("chapter") == chapter_key and not t["is_chapter"]]
        for member in sorted(members, key=lambda t: t["index"]):
            if st.button(
                member["key"],
                key=f"mdf-topic-{member['key']}",
                use_container_width=True,
                type="primary" if selected == member["key"] else "secondary",
            ):
                navigate_to(member["key"])


def mdf_reference():
    """Render the MDF Reference page (chapter-grouped browser + detail pane)."""
    import streamlit as st

    from src.frontend.ui_utils import apply_standard_layout_css

    apply_standard_layout_css()

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
        st.caption(f"{len(topics)} topics · MDF 1.9a field reference")
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
        meta_bits = [f"key {topic['key']}"]
        if topic.get("chapter"):
            meta_bits.append(f"chapter {topic['chapter']}")
        meta_bits.append(f"source line {topic['line']}")
        st.caption(" · ".join(meta_bits))
        for block in topic["blocks"]:
            marker = block["marker"]
            text = block["text"]
            if marker == "shd":
                continue  # the heading is rendered above
            if marker in ("shd2", "shd3", "shd4"):
                level = {"shd2": "#### ", "shd3": "##### ", "shd4": "###### "}[marker]
                st.markdown(level + md_escape(strip_marker(text).strip()))
            elif marker in ("ftx", "fxv"):
                st.code(strip_marker(text), language=None)
            elif marker == "cf":
                st.caption("→ " + md_escape(strip_marker(text)).strip())
                targets = block.get("targets") or []
                resolved, missing = split_cf_targets(targets, set(topics_by_key))
                for t in missing:
                    st.button(
                        f"⚠ {t} — topic not found",
                        key=f"mdf-cf-missing-{selected}-{t}",
                        disabled=True,
                        help="The source names this cross-reference target, but no such topic exists.",
                        use_container_width=True,
                    )
                for row_start in range(0, len(resolved), _CF_ROW_WIDTH):
                    row = resolved[row_start : row_start + _CF_ROW_WIDTH]
                    cols = st.columns(len(row))
                    for col, target in zip(cols, row):
                        if col.button(
                            target,
                            key=f"mdf-cf-{selected}-{row_start}-{target}",
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


if __name__ == "__main__":
    mdf_reference()