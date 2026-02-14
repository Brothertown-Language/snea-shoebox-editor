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
            f"Checking again in {poll_delay}s... (Attempt {i+1}/{max_polls})"
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
    lines = mdf_text.split('\n')
    
    line_html_parts = []
    for i, line in enumerate(lines):
        diag = diagnostics[i] if diagnostics and i < len(diagnostics) else {"status": "ok"}
        status_cls = f"status-{diag['status']}"
        msg = diag.get("message", "")
        escaped_line = _html.escape(line) if line else "&nbsp;"
        
        # Build line with optional tooltip/highlight
        title_attr = f'title="{_html.escape(msg)}"' if msg else ""
        line_html_parts.append(
            f'<div class="mdf-line {status_cls}" {title_attr}>{escaped_line}</div>'
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
        .mdf-line.status-error {{
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff4b4b;
        }}
        .mdf-line.status-warning {{
            background-color: rgba(255, 165, 0, 0.1);
            border-left: 3px solid #ffa500;
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


# ── Sidebar Utilities ──────────────────────────────────────────────────


def get_mdf_rich_html(mdf_text: str) -> str:
    """Return an HTML representation of MDF data suitable for rich-text clipboard."""
    import html as _html
    lines = mdf_text.split('\n')
    line_html = []
    for line in lines:
        if not line.strip():
            line_html.append("<br>")
            continue
        escaped = _html.escape(line)
        # Basic structural highlighting for tags
        if line.startswith('\\'):
            parts = escaped.split(' ', 1)
            tag = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            line_html.append(f'<div><b style="color: #cc6622;">{tag}</b> {content}</div>')
        else:
            line_html.append(f'<div>{escaped}</div>')
    
    return f'<div style="font-family: monospace; white-space: pre-wrap;">{"".join(line_html)}</div>'


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
        </style>
        """
    )


# ── Page Utilities ─────────────────────────────────────────────────────


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
