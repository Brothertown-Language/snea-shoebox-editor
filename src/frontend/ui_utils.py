# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
UI utilities for Streamlit components.
"""
import time
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components
from src.frontend.constants import GH_AUTH_TOKEN_COOKIE


# ── Error Handling ─────────────────────────────────────────────────────


def handle_ui_error(e: Exception, user_message: str = "An unexpected error occurred.",
                    logger_name: Optional[str] = None):
    """
    Standardized error handler for UI-facing code.
    Logs the full stack trace to server logs and shows a sanitized message to the user.

    Args:
        e: The exception that occurred.
        user_message: A safe, user-friendly message to display in the UI.
        logger_name: Optional name for the logger. If None, uses the calling module's name.
    """
    from src.logging_config import get_logger
    from src.database.connection import is_production

    # 1. Server-side logging (Full trace)
    log = get_logger(logger_name or "ui_error_handler")
    log.error(f"{user_message} Detail: {str(e)}", exc_info=True)

    # 2. UI Display (Sanitized)
    st.error(user_message)
    if str(e):
        st.warning(str(e))
    if not is_production():
        st.info("💡 *Full stack trace available in server logs (tmp/streamlit.log).*")


# ── Infrastructure Dialogs ─────────────────────────────────────────────


@st.dialog("Database Starting")
def show_startup_dialog(config: Dict[str, str], initial_status: str):
    """Display a dialog with the database startup status."""
    from src.services.infrastructure_service import InfrastructureService

    st.write(f"The production database is currently **{initial_status}**.")

    if initial_status == "POWEROFF":
        st.write("Sending start command...")
        if not InfrastructureService.start_service(config):
            st.error("Failed to send start command. Please contact support.")
            return
        st.write("Start command sent. Waiting for database to become active...")

    max_polls = 60
    poll_delay = 10

    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    current_status = initial_status
    for i in range(max_polls):
        current_status = InfrastructureService.get_service_status(config)

        dns_ok = True
        if current_status == "RUNNING":
            from urllib.parse import urlparse
            from src.database import get_db_url
            url = get_db_url()
            if url:
                parsed = urlparse(url)
                host = parsed.hostname
                if host:
                    dns_ok, _, _, _ = InfrastructureService.verify_dns(host)

        if current_status == "RUNNING" and dns_ok:
            status_placeholder.success("Database is now online!")
            progress_bar.progress(100)
            time.sleep(2)
            st.rerun()
            return

        display_status = current_status
        if current_status == "RUNNING" and not dns_ok:
            display_status = "RUNNING (Waiting for DNS)"

        status_placeholder.info(
            f"Current Status: **{display_status or 'Unknown'}**\n\n"
            f"Checking again in {poll_delay}s... (Attempt {i + 1}/{max_polls})"
        )
        progress_bar.progress((i + 1) / max_polls)
        time.sleep(poll_delay)

    if current_status == "REBUILDING":
        st.rerun()

    st.error("The production database is taking too long to start. Please try refreshing the page in a few minutes.")


@st.dialog("Missing Secrets")
def show_secrets_missing_dialog(missing_secrets: list[str]):
    """Display a dialog listing missing mandatory secrets."""
    st.error("The application cannot start because one or more mandatory secrets are missing.")
    st.write("Please ensure the following secrets are configured in Streamlit Cloud or `.streamlit/secrets.toml`:")
    for secret in missing_secrets:
        st.markdown(f"- `{secret}`")

    st.info("After adding the secrets, please refresh the page.")
    if st.button("I've added the secrets, refresh now"):
        st.rerun()


def ensure_secrets_present():
    """Verify that all mandatory secrets are present. Blocks execution if any are missing."""
    from src.services.infrastructure_service import InfrastructureService

    missing = InfrastructureService.get_missing_secrets()
    if missing:
        show_secrets_missing_dialog(missing)
        st.stop()


def ensure_db_alive():
    """Check if DB is alive, start it if not, and show dialog until ready."""
    from src.services.infrastructure_service import InfrastructureService

    is_alive, status = InfrastructureService.check_db_alive()
    if is_alive:
        return

    config = InfrastructureService.get_aiven_config()
    if not config:
        return

    if status in ["POWEROFF", "REBUILDING", "STARTING_DNS"]:
        show_startup_dialog(config, "STARTING" if status == "STARTING_DNS" else status)
        st.stop()
    else:
        st.warning(f"Database is in an unexpected state: {status}. Access is blocked for safety.")
        st.stop()


# ── MDF Display Utilities ──────────────────────────────────────────────


def _arrow_svg(color: str) -> str:
    """Return a percent-encoded SVG arrow glyph for use in CSS url()."""
    from urllib.parse import quote
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
        f'<text x="0" y="42" font-size="48" font-weight="bold" fill="{color}">➥</text></svg>'
    )
    return quote(svg, safe='')


def render_mdf_block(mdf_text: str, key: str = "", diagnostics: Optional[List[Dict]] = None) -> None:
    """Render MDF data in a soft-wrapped <pre> block with structural highlighting.

    Lines that wrap display a continuation marker (↩) via a hanging indent.
    If 'diagnostics' is provided, lines are highlighted based on their status
    (error, warning, ok).
    """
    import html as _html
    from src.mdf.parser import format_mdf_record
    mdf_text = format_mdf_record(mdf_text)
    lines = mdf_text.split('\n')

    line_html_parts = []
    for i, line in enumerate(lines):
        diag = diagnostics[i] if diagnostics and i < len(diagnostics) else {"status": "ok"}
        status_cls = f"status-{diag['status']}"
        msg = diag.get("message", "")

        # Build inner HTML: use span-level markup when intra-line spans are available
        spans = diag.get("spans")
        if spans:
            inner_html = "".join(
                f'<mark class="diff-token">{_html.escape(s["text"])}</mark>'
                if s["changed"] else _html.escape(s["text"])
                for s in spans
            ) or "&nbsp;"
        else:
            inner_html = _html.escape(line) if line else "&nbsp;"

        # Build line with optional tooltip/highlight
        title_attr = f'title="{_html.escape(msg)}"' if msg else ""
        line_html_parts.append(
            f'<div class="mdf-line {status_cls}" {title_attr}>{inner_html}</div>'
        )

    line_divs = ''.join(line_html_parts)
    # st.html() renders inside an iframe that does NOT inherit Streamlit's
    # CSS custom properties.  We must read the theme colours from the parent
    # frame via JavaScript and apply them to the block.
    st.html(f"""
        <style>
        .mdf-wrap-block {{
            border: 1px solid #ccc;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            font-family: 'Source Code Pro', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            margin: 0;
        }}
        .mdf-line {{
            white-space: pre-wrap;
            word-break: break-word;
            overflow-wrap: break-word;
            /* Hanging indent: only soft-wrapped continuation lines are indented */
            padding-left: 2.5rem;
            text-indent: -2.5rem;
            /* SVG arrow for soft-wrap indicator */
            background-repeat: no-repeat;
            background-position: 0.1rem 1.5em;
            background-size: 2.2rem 1.5em;
        }}
        .mdf-line.status-suggestion {{
            background-color: rgba(255, 165, 0, 0.15);
            border-left: 3.5px solid #ffa500;
        }}
        .mdf-line.status-note {{
            background-color: rgba(0, 123, 255, 0.1);
            border-left: 3.5px solid #007bff;
        }}
        .mdf-line.status-error {{
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff4b4b;
        }}
        .mdf-line.status-warning {{
            background-color: rgba(255, 165, 0, 0.1);
            border-left: 3px solid #ffa500;
        }}
        .mdf-line.status-diff-changed {{
            background-color: rgba(255, 220, 0, 0.18);
            border-left: 3.5px solid #e6b800;
        }}
        .mdf-line.status-diff-added {{
            background-color: rgba(0, 180, 80, 0.15);
            border-left: 3.5px solid #00b450;
        }}
        .mdf-line.status-diff-removed {{
            background-color: rgba(220, 50, 50, 0.13);
            border-left: 3.5px solid #dc3232;
        }}
        mark.diff-token {{
            background-color: rgba(255, 180, 0, 0.55);
            color: inherit;
            border-radius: 2px;
            padding: 0 1px;
        }}
        /* Light theme arrow (deep orange on light bg) */
        @media (prefers-color-scheme: light) {{
            .mdf-wrap-block {{ color: #31333F; background-color: #f0f2f6; border-color: #31333F; }}
            .mdf-line {{ background-image: url("data:image/svg+xml,{_arrow_svg('#cc6622')}"); }}
        }}
        /* Dark theme arrow (bright orange on dark bg) */
        @media (prefers-color-scheme: dark) {{
            .mdf-wrap-block {{ color: #fafafa; background-color: #262730; border-color: #fafafa; }}
            .mdf-line {{ background-image: url("data:image/svg+xml,{_arrow_svg('#e8943a')}"); }}
        }}
        </style>
        <div class="mdf-wrap-block" id="mdf-block">{line_divs}</div>
        <script>
        (function() {{
            // Try to read actual Streamlit theme colors from parent frame
            var el = document.getElementById('mdf-block');
            try {{
                var parentEl = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (parentEl) {{
                    var cs = window.parent.getComputedStyle(parentEl);
                    var bg = cs.backgroundColor;
                    var fg = cs.color;
                    if (bg && fg) {{
                        el.style.color = fg;
                        el.style.backgroundColor = bg;
                        el.style.borderColor = fg;
                    }}
                }}
            }} catch(e) {{}}
        }})();
        </script>
    """)


def _is_diff_ignored_line(line: str) -> bool:
    """Return True for lines that should be excluded from diff comparison.

    Ignored: blank lines and the ``\\nt Record:`` annotation line.
    """
    stripped = line.strip()
    return stripped == '' or stripped.startswith(r'\nt Record:')


def _tokenize_line(line: str) -> list[str]:
    """Split a line into alternating non-whitespace/whitespace tokens.

    Returns a list of strings whose concatenation equals ``line``.
    """
    import re
    return re.split(r'(\s+)', line)


def _intra_line_spans(old_line: str, new_line: str) -> tuple[list[dict], list[dict]]:
    """Return (old_spans, new_spans) with word-level change markup.

    Each span is ``{"text": str, "changed": bool}``.  Whitespace-only
    differences are ignored unless there are no non-whitespace differences
    on that line pair.
    """
    import difflib

    old_tokens = _tokenize_line(old_line)
    new_tokens = _tokenize_line(new_line)

    # Determine whether any non-whitespace token differs
    old_content = [t for t in old_tokens if t.strip()]
    new_content = [t for t in new_tokens if t.strip()]
    has_content_diff = old_content != new_content

    def _build_spans(tokens: list[str], changed_indices: set[int]) -> list[dict]:
        return [{"text": t, "changed": i in changed_indices} for i, t in enumerate(tokens)]

    matcher = difflib.SequenceMatcher(None, old_tokens, new_tokens, autojunk=False)
    old_changed: set[int] = set()
    new_changed: set[int] = set()
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        for idx in range(i1, i2):
            tok = old_tokens[idx]
            # Skip whitespace tokens when content differences exist
            if has_content_diff and not tok.strip():
                continue
            old_changed.add(idx)
        for idx in range(j1, j2):
            tok = new_tokens[idx]
            if has_content_diff and not tok.strip():
                continue
            new_changed.add(idx)

    return _build_spans(old_tokens, old_changed), _build_spans(new_tokens, new_changed)


def compute_mdf_line_diffs(
        existing_text: str,
        new_text: str,
) -> tuple[list[dict], list[dict]]:
    """Compute per-line diff diagnostics for two MDF texts.

    Returns a tuple (existing_diags, new_diags) where each element is a list
    of diagnostic dicts suitable for passing to render_mdf_block().

    Blank lines and ``\\nt Record:`` lines are excluded from the diff so that
    added/removed blank lines and the record-id annotation do not produce
    spurious diff highlights.

    Statuses used:
      - ``ok``           — line is identical on both sides
      - ``diff-changed`` — line exists on both sides but content differs;
                           the dict also carries a ``spans`` key with
                           word-level change segments
      - ``diff-added``   — line is only in the new (uploaded) record
      - ``diff-removed`` — line is only in the existing record
    """
    import difflib
    from src.mdf.parser import format_mdf_record

    existing_lines = format_mdf_record(existing_text).split('\n')
    new_lines = format_mdf_record(new_text).split('\n')

    existing_diags: list[dict] = [{"status": "ok"}] * len(existing_lines)
    new_diags: list[dict] = [{"status": "ok"}] * len(new_lines)

    # Build filtered index lists — skip blank lines and \nt Record: lines
    existing_idx = [i for i, ln in enumerate(existing_lines) if not _is_diff_ignored_line(ln)]
    new_idx = [j for j, ln in enumerate(new_lines) if not _is_diff_ignored_line(ln)]

    existing_filtered = [existing_lines[i] for i in existing_idx]
    new_filtered = [new_lines[j] for j in new_idx]

    matcher = difflib.SequenceMatcher(None, existing_filtered, new_filtered, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            pass
        elif tag == 'replace':
            # Pair up changed lines for intra-line span computation
            paired = list(zip(range(i1, i2), range(j1, j2)))
            paired_fi = {fi for fi, _ in paired}
            paired_fj = {fj for _, fj in paired}
            for fi, fj in paired:
                old_line = existing_filtered[fi]
                new_line = new_filtered[fj]
                old_spans, new_spans = _intra_line_spans(old_line, new_line)
                existing_diags[existing_idx[fi]] = {"status": "diff-changed", "spans": old_spans}
                new_diags[new_idx[fj]] = {"status": "diff-changed", "spans": new_spans}
            # Unpaired lines (when block sizes differ) get plain diff-changed
            for fi in range(i1, i2):
                if fi not in paired_fi:
                    existing_diags[existing_idx[fi]] = {"status": "diff-changed"}
            for fj in range(j1, j2):
                if fj not in paired_fj:
                    new_diags[new_idx[fj]] = {"status": "diff-changed"}
        elif tag == 'delete':
            for fi in range(i1, i2):
                existing_diags[existing_idx[fi]] = {"status": "diff-removed"}
        elif tag == 'insert':
            for fj in range(j1, j2):
                new_diags[new_idx[fj]] = {"status": "diff-added"}

    return existing_diags, new_diags


# ── Sidebar Utilities ──────────────────────────────────────────────────


def hide_sidebar_nav() -> None:
    """Hide the default Streamlit sidebar navigation links."""
    st.html(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """
    )


def apply_standard_layout_css() -> None:
    """
    Applies standard SNEA layout CSS for consistent padding and margins.
    Reduces block container padding on large screens and fixes status widget spacing.
    """
    import streamlit as st
    st.html(
        """
        <style>
        /* Custom class for ultra-tight horizontal padding on large screens */
        @media (min-width: calc(736px + 8rem)) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }
        
        /* st.status widget default styling - no overlay */
        div[data-testid="stStatusWidget"] {
            margin-bottom: 1rem !important;
        }

        /* Toolbar: hidden by default, visible on hover; click-through when hidden */
        header[data-testid="stHeader"] {
            opacity: 0 !important;
            transition: opacity 0.2s ease;
            right: 14px !important;
            pointer-events: none !important;
        }
        header[data-testid="stHeader"]:hover {
            opacity: 1 !important;
            pointer-events: auto !important;
        }
        header[data-testid="stHeader"] * {
            pointer-events: none !important;
        }
        header[data-testid="stHeader"]:hover * {
            pointer-events: auto !important;
        }

        /* Only modify scrollbars when hovered */
        *::-webkit-scrollbar:hover {
            width: 14px;
            height: 14px;
        }
        
        *::-webkit-scrollbar-thumb:hover {
            background-color: #555 !important;
            border-radius: 8px;
            border: 3px solid #e0e0e0;
        }
        
        *::-webkit-scrollbar-track:hover {
            background: #e0e0e0;
        }
        
        /* Firefox: only change hover behavior */
        * {
            scrollbar-width: thin;
        }
        
        *:hover {
            scrollbar-width: auto;
            scrollbar-color: #555 #e0e0e0;
        }

        </style>
        """
    )


# ── Page Utilities ─────────────────────────────────────────────────────


def render_back_to_main_button() -> None:
    """
    Renders a consistent 'Back to Main Menu' button in the sidebar.
    Uses centralized Page objects from NavigationService to prevent broken links.
    """
    from src.services.navigation_service import NavigationService
    if st.button("Back to Main Menu", icon="⬅️", use_container_width=True, key="nav_back_to_main"):
        st.switch_page(NavigationService.PAGE_HOME)


def reload_page_at_root(delay_ms: int = 0) -> None:
    js_code = f"""
        <script>
            // Clear the auth cookie
            document.cookie = "{GH_AUTH_TOKEN_COOKIE}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "{GH_AUTH_TOKEN_COOKIE}=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";

            function reloadPageAtRoot() {{
                try {{
                    // Navigate the TOP-LEVEL window, not the iframe
                    window.top.location.href = "/";
                }} catch (e) {{
                    // Fallback: force top-level reload
                    window.top.location.reload();
                }}
            }}

            {f"setTimeout(reloadPageAtRoot, {delay_ms});" if delay_ms > 0 else "reloadPageAtRoot();"}
        </script>
    """
    components.html(js_code, height=0)
