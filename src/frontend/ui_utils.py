# Copyright (c) 2026 Brothertown Language
"""
UI utilities for Streamlit components.
"""
import streamlit as st
import streamlit.components.v1 as components
from src.frontend.constants import GH_AUTH_TOKEN_COOKIE

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
