# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import datetime as _dt
import io
import json
import zipfile

import streamlit as st


class _RecordSearchResultLike:
    """Page-local container matching the RecordSearchResult field contract
    (records, total_count, limit, offset) for seam-consumed semantic results.
    UI-level shim only — binds to the SemanticSearchResult contract (R-8),
    never to pgvector or ORM internals."""

    def __init__(self, records, total_count, limit, offset, matched_terms=None):
        self.records = records
        self.total_count = total_count
        self.limit = limit
        self.offset = offset
        self.matched_terms = matched_terms


def records():
    from src.frontend.search_highlight import compute_fts_spans, compute_term_spans
    from src.frontend.ui_utils import (
        apply_standard_layout_css,
        compute_mdf_line_diffs,
        handle_ui_error,
        hide_sidebar_nav,
        render_back_to_main_button,
        render_mdf_block,
    )
    from src.mdf.parser import format_mdf_record
    from src.mdf.validator import MDFValidator
    from src.services.identity_service import IdentityService
    from src.services.linguistic_service import LinguisticService
    from src.services.navigation_service import NavigationService
    from src.services.preference_service import PreferenceService
    from src.services.semantic_search_service import CALIBRATED_FLOOR, search_semantic
    from src.services.upload_service import UploadService

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()
    apply_standard_layout_css()

    user_email = st.session_state.get("user_email")
    user_role = st.session_state.get("user_role", "viewer")

    # DEBUG: Show user role to verify access
    # st.sidebar.info(f"DEBUG: Role={user_role}")

    # --- 1. Load Initial State from Preferences ---
    # Check for clear-search request (must run before widget creation)
    if st.session_state.pop("_clear_search", False):
        st.session_state.search_query = ""
        st.session_state.current_page = 1
        st.session_state._search_input_key = st.session_state.get("_search_input_key", 0) + 1

    # Load persistence preferences
    if user_email:
        if "page_size" not in st.session_state:
            saved_size = PreferenceService.get_preference(user_email, "records", "page_size", "25")
            st.session_state.page_size = int(saved_size) if saved_size is not None else 25

        if "structural_highlighting" not in st.session_state:
            saved_hl = PreferenceService.get_preference(user_email, "records", "structural_highlighting", "True")
            st.session_state.structural_highlighting = saved_hl == "True"

    # Defaults if still missing
    if "page_size" not in st.session_state:
        st.session_state.page_size = 25
    if "semantic_threshold" not in st.session_state:
        # SC-9 (Issue #1400): fresh-session default is the published calibrated
        # floor from the calibration concern — no magic-number duplication.
        saved_threshold = None
        if user_email:
            saved_threshold = PreferenceService.get_preference(
                user_email, "records", "semantic_threshold", str(CALIBRATED_FLOOR)
            )
        if saved_threshold is None:
            saved_threshold = str(CALIBRATED_FLOOR)
        try:
            parsed_threshold = float(saved_threshold)
        except (TypeError, ValueError):
            parsed_threshold = CALIBRATED_FLOOR
        if not (0.0 <= parsed_threshold <= 1.0):
            parsed_threshold = CALIBRATED_FLOOR
        st.session_state.semantic_threshold = parsed_threshold

    # SC-3 (Issue #1385, R-3): validation guard for the semantic threshold
    # backing value. Runs on every page execution BEFORE widget instantiation
    # and BEFORE any set_preference persistence step. Non-numeric or
    # out-of-range backing values are rejected and the last accepted value is
    # restored; the pre-instantiation sync block below then re-syncs both
    # coupled widget keys from the corrected backing value. The guard itself
    # never calls set_preference, so an invalid edit is never persisted.
    _THRESHOLD_MIN = 0.0
    _THRESHOLD_MAX = 1.0

    if "_accepted_threshold" not in st.session_state:
        st.session_state._accepted_threshold = st.session_state.semantic_threshold

    def _validate_threshold():
        """Reject a non-numeric or out-of-range semantic_threshold edit.

        Returns True when the backing value is valid (and is recorded as the
        last accepted value); False when an invalid value was rejected and the
        last accepted value restored.
        """
        raw = st.session_state.get("semantic_threshold")
        is_valid = (
            not isinstance(raw, bool) and isinstance(raw, (int, float)) and _THRESHOLD_MIN <= raw <= _THRESHOLD_MAX
        )
        if not is_valid:
            st.session_state.semantic_threshold = st.session_state._accepted_threshold
            return False
        st.session_state._accepted_threshold = raw
        return True

    _validate_threshold()

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_mode" not in st.session_state:
        st.session_state.search_mode = "Headword"
    if "selected_source_id" not in st.session_state:
        st.session_state.selected_source_id = "All Sources"
    if "global_edit_mode" not in st.session_state:
        st.session_state.global_edit_mode = False
    if "is_locked_filter" not in st.session_state:
        st.session_state.is_locked_filter = "All"
    if "selected_language_id" not in st.session_state:
        st.session_state.selected_language_id = "All Languages"
    if "language_role_filter" not in st.session_state:
        st.session_state.language_role_filter = "Any"
    if "pending_edits" not in st.session_state:
        st.session_state.pending_edits = {}
    if "local_edits" not in st.session_state:
        st.session_state.local_edits = set()
    if "view_selection_only" not in st.session_state:
        st.session_state.view_selection_only = False
    if "structural_highlighting" not in st.session_state:
        st.session_state.structural_highlighting = True
    if "confirm_delete_id" not in st.session_state:
        st.session_state.confirm_delete_id = None
    if "selection" not in st.session_state:
        # Try to load selection from persistence
        st.session_state.selection = []
        if user_email:
            selection_json = PreferenceService.get_preference(user_email, "global", "selection_contents", "[]")
            if selection_json is None:
                selection_ids = []
            else:
                try:
                    selection_ids = json.loads(selection_json)
                    if selection_ids:
                        loaded_records = []
                        for rid in selection_ids:
                            rec = LinguisticService.get_record(rid)
                            if rec:
                                loaded_records.append(rec)
                        st.session_state.selection = loaded_records
                except Exception as e:
                    handle_ui_error(e, f"Failed to load selection for {user_email}", logger_name="snea.pages.records")

    def on_search_change():
        input_key = f"search_query_input_{st.session_state.get('_search_input_key', 0)}"
        st.session_state.search_query = st.session_state.get(input_key, "")
        st.session_state.current_page = 1

    def on_mode_change():
        st.session_state.search_mode = st.session_state.search_mode_radio
        st.session_state.current_page = 1

    def on_source_change():
        sources = LinguisticService.get_sources_with_counts()
        source_id_map = {s["name"]: s["id"] for s in sources}
        selected_name = st.session_state.source_select
        st.session_state.selected_source_id = source_id_map.get(selected_name, "All Sources")
        st.session_state.current_page = 1

    def on_language_change():
        languages = LinguisticService.get_languages()
        lang_id_map = {lang["name"]: lang["id"] for lang in languages}
        selected_name = st.session_state.language_select
        st.session_state.selected_language_id = lang_id_map.get(selected_name, "All Languages")
        st.session_state.current_page = 1

    def on_language_role_change():
        st.session_state.language_role_filter = st.session_state.language_role_radio
        st.session_state.current_page = 1

    # --- 2. Calculate Search Results (Pre-calculate for Header Count) ---
    source_filter_id = (
        None if st.session_state.selected_source_id == "All Sources" else int(st.session_state.selected_source_id)
    )
    search_term = st.session_state.search_query if st.session_state.search_query else None

    # Fetch records for current page
    limit = st.session_state.page_size
    offset = (st.session_state.current_page - 1) * limit

    selection_record_ids = (
        [r["id"] for r in st.session_state.selection] if st.session_state.view_selection_only else None
    )

    # Map is_locked_filter to boolean
    is_locked_bool = None
    if st.session_state.is_locked_filter == "Locked":
        is_locked_bool = True
    elif st.session_state.is_locked_filter == "Unlocked":
        is_locked_bool = False

    language_filter_id = (
        None if st.session_state.selected_language_id == "All Languages" else int(st.session_state.selected_language_id)
    )
    language_role_map = {"Any": None, "Primary": "primary", "Secondary": "secondary"}
    language_role_val = language_role_map.get(st.session_state.language_role_filter)

    # SC-7 (Issue #1385, R-7/R-8): per-mode dispatch. Semantic modes consume
    # the #36 seam (search_semantic → SemanticSearchResult) directly — the
    # page passes the session threshold and maps the ranked (record_id, score)
    # list to full records; exact-match modes keep the existing search_records
    # path byte-identical. The UI binds to the seam contract only — no
    # pgvector or ORM imports.
    is_semantic_mode = st.session_state.search_mode in ("Semantic Gloss", "Semantic All")

    search_result = None
    semantic_scores: dict[int, float] = {}

    # SC-6 (Issue #1385, R-6): degraded-state payload from the semantic seam.
    # Non-"ok" statuses render a designated clean empty state in the MAIN
    # panel and never fall through to record rendering or a crash.
    semantic_status = None

    if is_semantic_mode:
        if search_term:
            mode_key = "gloss" if st.session_state.search_mode == "Semantic Gloss" else "all"
            # Rank-once pagination (R-5, SC-5): the seam ranks the full
            # result list once per distinct (mode, query, threshold, source)
            # digest; page navigation slices the cached ranked list — the
            # service is NOT re-invoked on navigation.
            semantic_digest = (
                mode_key,
                search_term,
                float(st.session_state.semantic_threshold),
                source_filter_id,
            )
            semantic_matched_terms = None
            cached_ranked = st.session_state.get("_semantic_ranked_cache")
            if cached_ranked is None or cached_ranked[0] != semantic_digest:
                semantic_result = search_semantic(
                    mode=mode_key,
                    query=search_term,
                    threshold=st.session_state.semantic_threshold,
                    source_id=source_filter_id,
                    limit=None,
                )
                # SC-6: a degraded (non-ok) payload is never cached as a
                # ranked list — re-search retries the seam.
                if getattr(semantic_result, "status", "ok") == "ok":
                    # SC-20 (revised): thread per-record matched source-field
                    # terms alongside the ranked pairs so the page-local
                    # result container can carry them for span computation.
                    semantic_matched_terms = getattr(semantic_result, "matched_terms", None)
                    cached_ranked = (
                        semantic_digest,
                        sorted(semantic_result.results, key=lambda p: (-p[1], p[0])),
                        semantic_matched_terms,
                    )
                    st.session_state._semantic_ranked_cache = cached_ranked
                    semantic_status = None
                else:
                    semantic_status = semantic_result.status
                    cached_ranked = (semantic_digest, [], None)
                    st.session_state._semantic_ranked_cache = cached_ranked
            elif cached_ranked[1]:
                ranked_pairs = cached_ranked[1]
            else:
                # Degraded payload cached from this same digest — re-consume
                # the seam once to re-derive the status for rendering.
                semantic_result = search_semantic(
                    mode=mode_key,
                    query=search_term,
                    threshold=st.session_state.semantic_threshold,
                    source_id=source_filter_id,
                    limit=None,
                )
                if getattr(semantic_result, "status", "ok") != "ok":
                    semantic_status = semantic_result.status
                ranked_pairs = []
                semantic_matched_terms = getattr(semantic_result, "matched_terms", None)
            if semantic_status is None and cached_ranked is not None:
                ranked_pairs = cached_ranked[1]
                semantic_matched_terms = cached_ranked[2]
            else:
                ranked_pairs = []
            semantic_scores = dict(ranked_pairs)
            # Rank-once pagination (R-5, SC-5): slice the cached ranked list
            # first, then hydrate only the current page's records — the
            # service is not re-invoked on page navigation.
            page_pairs = ranked_pairs[offset : offset + limit]
            page_records = []
            for record_id, _score in page_pairs:
                rec = LinguisticService.get_record(record_id)
                if rec:
                    page_records.append(rec)
            search_result = _RecordSearchResultLike(
                records=page_records,
                total_count=len(ranked_pairs),
                limit=limit,
                offset=offset,
                matched_terms=semantic_matched_terms,
            )
        else:
            # No query in a semantic mode: match exact-mode empty-query
            # behavior (search term None → no strategy, unfiltered browse).
            search_result = LinguisticService.search_records(
                source_id=source_filter_id,
                language_id=None,
                language_role=None,
                is_locked=is_locked_bool,
                search_term=None,
                search_mode=st.session_state.search_mode,
                record_ids=selection_record_ids,
                limit=limit,
                offset=offset,
            )
    else:
        search_result = LinguisticService.search_records(
            source_id=source_filter_id,
            language_id=language_filter_id,
            language_role=language_role_val,
            is_locked=is_locked_bool,
            search_term=search_term,
            search_mode=st.session_state.search_mode,
            record_ids=selection_record_ids,
            limit=limit,
            offset=offset,
        )

    records_batch = search_result.records
    total_count = search_result.total_count
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1

    # Ensure current page is within bounds
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = max(1, total_pages)
        st.rerun()

    has_next = st.session_state.current_page < total_pages

    # --- 3. Sidebar: Filters & Navigation ---
    with st.sidebar:
        # Compact Search Controls
        st.html("""
            <style>
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
                gap: 0.5rem !important;
            }
            </style>
        """)

        header_text = f"Search: {st.session_state.search_mode} ({total_count} records)" if search_term else ""
        if st.session_state.view_selection_only:
            header_text = f"Selection Contents ({total_count} records)"
        if header_text:
            st.markdown(f"**{header_text}**")

        search_input_key = f"search_query_input_{st.session_state.get('_search_input_key', 0)}"
        st.text_input(
            "Search terms...",
            value=st.session_state.search_query,
            key=search_input_key,
            label_visibility="collapsed",
            on_change=on_search_change,
        )

        # Search Mode: Vertical Radio with Dynamic Caption
        SEARCH_MODE_CAPTIONS = {
            "Headword": "Algonquian headwords and variants (\\lx, \\va)",
            "Gloss": "Primary English glosses (\\ge)",
            "Lexeme": "All Algonquian terms",
            "FTS": "Every field",
            "Semantic Gloss": "Semantic search over English glosses",
            "Semantic All": "Semantic search over all fields",
        }
        st.radio(
            "Search Mode",
            ["Headword", "Gloss", "Lexeme", "FTS", "Semantic Gloss", "Semantic All"],
            index=["Headword", "Gloss", "Lexeme", "FTS", "Semantic Gloss", "Semantic All"].index(
                st.session_state.search_mode
            ),
            key="search_mode_radio",
            label_visibility="collapsed",
            on_change=on_mode_change,
        )
        st.caption(SEARCH_MODE_CAPTIONS.get(st.session_state.search_mode, ""))
        is_fts_mode = st.session_state.search_mode == "FTS"

        threshold_help = None if is_semantic_mode else "Applies only in Semantic modes."

        # Two-way coupled threshold widgets: both keys are bound to the shared
        # backing value st.session_state.semantic_threshold. Sync happens
        # pre-instantiation (never after widget instantiation) and edits are
        # propagated through on_change callbacks — no post-instantiation
        # session_state writes to widget keys, no st.rerun().
        if "semantic_threshold_slider" not in st.session_state:
            st.session_state.semantic_threshold_slider = st.session_state.semantic_threshold
        if "semantic_threshold_number" not in st.session_state:
            st.session_state.semantic_threshold_number = st.session_state.semantic_threshold
        if st.session_state.semantic_threshold_slider != st.session_state.semantic_threshold:
            st.session_state.semantic_threshold_slider = st.session_state.semantic_threshold
        if st.session_state.semantic_threshold_number != st.session_state.semantic_threshold:
            st.session_state.semantic_threshold_number = st.session_state.semantic_threshold

        def on_threshold_slider_change():
            effective = float(st.session_state.semantic_threshold_slider)
            st.session_state.semantic_threshold = effective
            if user_email:
                PreferenceService.set_preference(user_email, "records", "semantic_threshold", str(effective))

        def on_threshold_number_change():
            effective = float(st.session_state.semantic_threshold_number)
            st.session_state.semantic_threshold = effective
            if user_email:
                PreferenceService.set_preference(user_email, "records", "semantic_threshold", str(effective))

        threshold_slider = st.container()
        threshold_slider.slider(
            "Semantic threshold",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="semantic_threshold_slider",
            value=st.session_state.semantic_threshold,
            on_change=on_threshold_slider_change,
            label_visibility="collapsed",
            disabled=not is_semantic_mode,
            help=threshold_help,
        )
        threshold_number = st.container()
        threshold_number.number_input(
            "Semantic threshold",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="semantic_threshold_number",
            value=st.session_state.semantic_threshold,
            on_change=on_threshold_number_change,
            label_visibility="collapsed",
            disabled=not is_semantic_mode,
            help=threshold_help,
        )
        search_col1, search_col2 = st.columns(2)
        if search_col1.button("", icon="🔍", key="search_trigger", help="Execute Search", use_container_width=True):
            input_key = f"search_query_input_{st.session_state.get('_search_input_key', 0)}"
            st.session_state.search_query = st.session_state.get(input_key, "")
            st.session_state.current_page = 1
            st.rerun()
        if search_col2.button("", icon="❌", key="search_clear", help="Clear Search", use_container_width=True):
            st.session_state._clear_search = True
            st.session_state.current_page = 1
            st.rerun()

        sources = LinguisticService.get_sources_with_counts()
        source_options = ["All Sources"] + [s["name"] for s in sources]
        source_name_map = {str(s["id"]): s["name"] for s in sources}
        source_name_map["All Sources"] = "All Sources"

        current_source_name = source_name_map.get(str(st.session_state.selected_source_id), "All Sources")
        st.selectbox(
            "Select Source",
            source_options,
            index=source_options.index(current_source_name),
            key="source_select",
            label_visibility="collapsed",
            on_change=on_source_change,
        )

        # Language Filter
        languages = LinguisticService.get_languages()
        lang_options = ["All Languages"] + [lang["name"] for lang in languages]
        lang_name_map = {str(lang["id"]): lang["name"] for lang in languages}
        current_lang_name = lang_name_map.get(str(st.session_state.selected_language_id), "All Languages")
        # SC-8 (Issue #1385, R-9): language filters are inert in semantic
        # modes — the semantic seam accepts only source_id. Disabled-filter
        # idiom mirrors FTS mode; previously-selected values are preserved
        # but no language constraint is applied to result expectations.
        if is_fts_mode:
            language_disabled_help = "Language filters are not available in Full-Text Search mode."
            language_role_disabled_help = "Language Role filters are not available in Full-Text Search mode."
        elif is_semantic_mode:
            language_disabled_help = "Language filters are not applied in Semantic search modes."
            language_role_disabled_help = "Language Role filters are not applied in Semantic search modes."
        else:
            language_disabled_help = None
            language_role_disabled_help = None
        st.selectbox(
            "Select Language",
            lang_options,
            index=lang_options.index(current_lang_name),
            key="language_select",
            label_visibility="collapsed",
            on_change=on_language_change,
            disabled=is_fts_mode or is_semantic_mode,
            help=language_disabled_help,
        )
        role_options = ["Any", "Primary", "Secondary"]
        st.radio(
            "Language Role",
            role_options,
            index=role_options.index(st.session_state.language_role_filter),
            key="language_role_radio",
            horizontal=True,
            label_visibility="collapsed",
            on_change=on_language_role_change,
            disabled=is_fts_mode or is_semantic_mode,
            help=language_role_disabled_help,
        )

        # Is Locked Filter
        lock_options = ["All", "Locked", "Unlocked"]
        st.radio(
            "Status: Locked",
            lock_options,
            index=lock_options.index(st.session_state.is_locked_filter),
            key="is_locked_filter",
            horizontal=True,
            label_visibility="collapsed",
        )

        c1, c2 = st.columns(2)
        if c1.button("Prev", icon="◀️", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            if st.session_state.global_edit_mode and st.session_state.pending_edits:
                for rid, mdf in st.session_state.pending_edits.items():
                    LinguisticService.update_record(
                        record_id=rid, user_email=user_email, mdf_data=mdf, change_summary="Auto-save via pagination"
                    )
                st.session_state.pending_edits = {}
            st.session_state.current_page -= 1
            st.rerun()
        if c2.button("Next", icon="▶️", disabled=not has_next, use_container_width=True):
            if st.session_state.global_edit_mode and st.session_state.pending_edits:
                for rid, mdf in st.session_state.pending_edits.items():
                    LinguisticService.update_record(
                        record_id=rid, user_email=user_email, mdf_data=mdf, change_summary="Auto-save via pagination"
                    )
                st.session_state.pending_edits = {}
            st.session_state.current_page += 1
            st.rerun()

        st.markdown(
            f"<p style='text-align: center; margin-bottom: 0;'>"
            f"Page {st.session_state.current_page} of {total_pages}</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align: center; font-size: 0.8em; color: gray;'>"
            f"Showing {offset + 1}-{min(offset + len(records_batch), total_count)}"
            f" of {total_count}</p>",
            unsafe_allow_html=True,
        )

        new_page_size = st.selectbox(
            "Results per page", [1, 5, 10, 25, 50, 100], index=[1, 5, 10, 25, 50, 100].index(st.session_state.page_size)
        )
        if new_page_size != st.session_state.page_size:
            st.session_state.page_size = new_page_size
            st.session_state.current_page = 1
            if user_email:
                PreferenceService.set_preference(user_email, "records", "page_size", str(new_page_size))
            st.rerun()

        # Moved Editing Controls here
        if user_role in ["editor", "admin"]:
            if not st.session_state.global_edit_mode:
                if st.button("Enter Edit Mode", icon="📝", use_container_width=True):
                    st.session_state.global_edit_mode = True
                    st.rerun()
            else:
                col_e1, col_e2 = st.columns(2)
                if col_e1.button("Cancel All", icon="❌", use_container_width=True):
                    st.session_state.global_edit_mode = False
                    st.session_state.pending_edits = {}
                    st.rerun()
                if col_e2.button("Save All", icon="💾", type="primary", use_container_width=True):
                    save_errors = []
                    skipped_locked = []
                    for rid, mdf in st.session_state.pending_edits.items():
                        # Explicit check for locked records during bulk save
                        rec = LinguisticService.get_record(rid)
                        if rec and rec.get("is_locked"):
                            skipped_locked.append(rid)
                            continue

                        success = LinguisticService.update_record(
                            record_id=rid,
                            user_email=user_email,
                            mdf_data=mdf,
                            change_summary="Bulk update via global edit mode",
                        )
                        if not success:
                            save_errors.append(rid)

                    if save_errors or skipped_locked:
                        error_msg = ""
                        if save_errors:
                            error_msg += f"Failed to save {len(save_errors)} records (IDs: {save_errors}). "
                        if skipped_locked:
                            error_msg += f"Skipped {len(skipped_locked)} locked records (IDs: {skipped_locked})."
                        st.error(error_msg)

                        # Keep only failed/skipped edits in pending_edits
                        st.session_state.pending_edits = {
                            rid: mdf
                            for rid, mdf in st.session_state.pending_edits.items()
                            if rid in save_errors or rid in skipped_locked
                        }
                    else:
                        st.session_state.pending_edits = {}
                        st.session_state.global_edit_mode = False
                        st.success("All changes saved!")
                    st.rerun()

            if st.button("⌨️ Direct Entry", use_container_width=True, help="Switch to Direct Record Entry mode"):
                st.switch_page(NavigationService.PAGE_DIRECT_ENTRY)
        else:
            st.info("View-only mode (Editor access required)")

        st.divider()
        structural_highlighting = st.toggle("Structural Highlighting", value=st.session_state.structural_highlighting)
        if structural_highlighting != st.session_state.structural_highlighting:
            st.session_state.structural_highlighting = structural_highlighting
            if user_email:
                PreferenceService.set_preference(
                    user_email, "records", "structural_highlighting", str(structural_highlighting)
                )
            st.rerun()

        st.divider()
        st.markdown(f"**My Selection** ({len(st.session_state.selection)} records)")

        selection_col1, selection_col2, selection_col3 = st.columns(3)

        view_icon = "📚" if st.session_state.view_selection_only else "🧺"
        view_help = (
            "Show all records" if st.session_state.view_selection_only else "Filter list to show only selected items"
        )
        if selection_col1.button("", icon=view_icon, use_container_width=True, help=view_help):
            st.session_state.view_selection_only = not st.session_state.view_selection_only
            st.session_state.current_page = 1
            st.rerun()

        if st.session_state.selection:
            # Generate MDF bundle text
            mdf_bundle = LinguisticService.bundle_records_to_mdf(st.session_state.selection)

            # Determine source name for filename
            sources = {r.get("source_name") for r in st.session_state.selection if r.get("source_name")}
            source_name = list(sources)[0] if len(sources) == 1 else "mixed"

            github_username = IdentityService.get_github_username(st.session_state.get("user_email"))

            fname = UploadService.generate_mdf_filename(
                prefix="selection",
                source_name=source_name,
                timestamp=_dt.datetime.now(),
                github_username=github_username,
            )

            selection_col2.download_button(
                label="📥",
                data=mdf_bundle,
                file_name=fname,
                mime="text/plain",
                use_container_width=True,
                help="Download selection as MDF",
            )

            if selection_col3.button("🗑️", use_container_width=True, help="Discard selection"):
                st.session_state.selection = []
                if user_email:
                    PreferenceService.set_preference(user_email, "global", "selection_contents", "[]")
                st.session_state.view_selection_only = False
                st.rerun()
        else:
            selection_col2.button("📥", disabled=True, use_container_width=True)
            selection_col3.button("🗑️", disabled=True, use_container_width=True)

        st.divider()

        # Determine what to export based on filters
        export_source_id = source_filter_id
        export_search_term = search_term
        export_record_ids = selection_record_ids

        # Semantic mode export (Issue #1385): the #36 strategy map routes the
        # semantic modes to the result-returning search_semantic seam, so any
        # strategy-map consumer (get_all_records_for_export /
        # stream_records_to_temp_file) re-dispatching with a semantic mode +
        # search term would crash (SemanticSearchResult has no order_by).
        # Respect the frozen service contract: derive export ids from the
        # already-ranked seam cache and pass them via record_ids — the
        # strategy dispatch is skipped entirely when record_ids is provided.
        # A zero-result semantic search (empty cache pairs, e.g. threshold
        # 1.0) must ALSO not re-dispatch — neutralize the term so the export
        # path browses nothing.
        semantic_export_ids = False
        if is_semantic_mode and not export_record_ids:
            cached = st.session_state.get("_semantic_ranked_cache")
            if cached is not None and cached[0][1] == (export_search_term or None):
                export_record_ids = [rid for rid, _score in cached[1]]
                semantic_export_ids = bool(search_term)

        # Prepare export data
        all_matching_records = LinguisticService.get_all_records_for_export(
            source_id=export_source_id,
            search_term=None if semantic_export_ids else (export_search_term or None),
            search_mode=st.session_state.search_mode,
            record_ids=export_record_ids,
        )

        distinct_sources = sorted({r["source_name"] for r in all_matching_records if r.get("source_name")})

        if all_matching_records:
            github_username = IdentityService.get_github_username(user_email)

            if len(distinct_sources) > 1:
                # Multiple sources: Zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for src_name in distinct_sources:
                        src_records = [r for r in all_matching_records if r["source_name"] == src_name]
                        if not src_records:
                            continue

                        mdf_content = LinguisticService.bundle_records_to_mdf(src_records)

                        # Generate individual filename for the entry in zip
                        entry_fname = UploadService.generate_mdf_filename(
                            prefix="export",
                            source_name=src_name,
                            timestamp=_dt.datetime.now(),
                            github_username=github_username,
                        )
                        zip_file.writestr(entry_fname, mdf_content)

                zip_filename = f"snea_export_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

                st.download_button(
                    label="Download All (Zip)",
                    data=zip_buffer.getvalue(),
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True,
                    help=(
                        f"Download {len(all_matching_records)} records"
                        f" from {len(distinct_sources)} sources as a ZIP of MDF files"
                    ),
                )
            else:
                # Single source: Direct MDF download via streaming to temp file
                source_name = distinct_sources[0] if distinct_sources else "results"

                fname = UploadService.generate_mdf_filename(
                    prefix="export",
                    source_name=source_name,
                    timestamp=_dt.datetime.now(),
                    github_username=github_username,
                )

                # Use streaming to temp file for better memory management
                temp_path = LinguisticService.stream_records_to_temp_file(
                    source_id=export_source_id,
                    search_term=None if semantic_export_ids else (export_search_term or None),
                    search_mode=st.session_state.search_mode,
                    record_ids=export_record_ids,
                )

                try:
                    with open(temp_path, "rb") as f:
                        file_bytes = f.read()
                        st.download_button(
                            label="Download Source (MDF)",
                            data=file_bytes,
                            file_name=fname,
                            mime="text/plain",
                            use_container_width=True,
                            help=f"Download {len(all_matching_records)} records from {source_name} as MDF (Streamed)",
                        )
                finally:
                    import os

                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            st.button("Download (Empty)", disabled=True, use_container_width=True)

        st.divider()
        render_back_to_main_button()

    # --- 4. Main Panel: Records List ---
    # SC-6 (Issue #1385, R-6): per-status clean empty states in the MAIN
    # panel records area — never a crash, never sidebar rendering. st.info
    # for informational states, st.warning for remedy-required states.
    # Theme-aware native elements only (no hex/rgba, no st.html).
    _BACKFILL_REMEDY = "Table Maintenance → Data Reprocessing → Embedding Backfill"

    if is_semantic_mode and search_term and semantic_status is not None:
        if semantic_status == "empty_query":
            st.info("Enter a query to search semantically.")
        elif semantic_status == "no_embeddings":
            st.warning(
                "No records have embeddings yet, so semantic search cannot match this query."
                f" An administrator can generate them via {_BACKFILL_REMEDY}."
            )
        elif semantic_status == "stale_model":
            st.warning(
                "The embedding model has changed since records were last processed, so"
                f" semantic results are unavailable. An administrator can resolve this"
                f" via {_BACKFILL_REMEDY}."
            )
        else:
            # Unknown status: fail clean, never crash.
            st.info("No records found matching your criteria.")
    elif not records_batch:
        if is_semantic_mode and search_term:
            # Zero-results-after-threshold (ok payload, empty ranking):
            # reuses the existing empty-batch branch with status-specific
            # copy naming the active threshold.
            st.info(
                "No records scored above the semantic threshold"
                f" ({float(st.session_state.semantic_threshold):.2f})."
                " Lower the Semantic threshold to widen the search."
            )
        else:
            st.info("No records found matching your criteria.")
    else:
        for record in records_batch:
            record_id = record["id"]
            mdf_data = format_mdf_record(record["mdf_data"])
            mdf_lines = mdf_data.split("\n")

            with st.container(border=True):
                is_locked = bool(record.get("is_locked", False))
                lock_status = " 🔒" if is_locked else ""
                # SC-4 (Issue #1385, R-4): semantic-mode rows append the
                # similarity score inline in the header line, fixed two
                # decimals, in the seam's descending-rank order; exact-match
                # modes render no score. Native markdown only — no hex/rgba.
                score_display = ""
                if is_semantic_mode and record_id in semantic_scores:
                    score_display = f" — Similarity: {semantic_scores[record_id]:.2f}"
                header_line = f"**Record #{record_id}** (Source: {record['source_name'] or 'Unknown'})"
                st.markdown(f"{header_line}{score_display}{lock_status}")

                # Check if it should be in edit mode (Global mode or local edit)
                # MUST NOT enter edit mode if locked.
                is_editing = False
                if not is_locked:
                    if st.session_state.global_edit_mode or record_id in st.session_state.local_edits:
                        is_editing = True

                if is_editing:
                    # Edit Mode: Record in text area
                    # Initialize pending_edits from record data if not present
                    initial_val = st.session_state.pending_edits.get(record_id, mdf_data)

                    edited_mdf = st.text_area(
                        "Edit MDF", value=initial_val, height=300, key=f"edit_{record_id}", label_visibility="collapsed"
                    )

                    # Update pending_edits if it changed
                    if edited_mdf != initial_val:
                        st.session_state.pending_edits[record_id] = edited_mdf

                    col_s1, col_s2, _ = st.columns([1, 1, 4])
                    if col_s1.button("Update", key=f"update_{record_id}", type="primary", use_container_width=True):
                        try:
                            summary = (
                                "Individual update"
                                if not st.session_state.global_edit_mode
                                else "Individual update in global edit mode"
                            )
                            success = LinguisticService.update_record(
                                record_id=record_id, user_email=user_email, mdf_data=edited_mdf, change_summary=summary
                            )
                            if success:
                                if record_id in st.session_state.pending_edits:
                                    del st.session_state.pending_edits[record_id]
                                if record_id in st.session_state.local_edits:
                                    st.session_state.local_edits.remove(record_id)
                                st.success(f"Record #{record_id} saved.")
                                st.rerun()
                            else:
                                if is_locked:
                                    st.error(f"Failed to save Record #{record_id}: Record is locked.")
                                else:
                                    msg = (
                                        f"Failed to save Record #{record_id}."
                                        " It may have been modified by another user."
                                    )
                                    st.error(msg)
                        except Exception as e:
                            handle_ui_error(e, "Error saving record", logger_name="snea.pages.records")

                    if not st.session_state.global_edit_mode:
                        if col_s2.button("Cancel", key=f"cancel_local_{record_id}", use_container_width=True):
                            if record_id in st.session_state.local_edits:
                                st.session_state.local_edits.remove(record_id)
                            if record_id in st.session_state.pending_edits:
                                del st.session_state.pending_edits[record_id]
                            st.rerun()

                else:
                    # View Mode
                    if is_locked and st.session_state.global_edit_mode:
                        st.warning("🔒 Record is locked and cannot be edited in global edit mode.")

                    diagnostics = None
                    if st.session_state.structural_highlighting:
                        diagnostics = MDFValidator.diagnose_record(mdf_lines)

                    # SC-17: thread query, mode, and computed highlight spans
                    # into the View-mode render call ONLY. Lexical modes use
                    # the service's matched raw terms (verbatim term spans);
                    # FTS mode derives spans from the query tokens via the
                    # single normalizer; SC-20 (revised): Semantic modes use
                    # the seam's per-record matched source-field terms with
                    # the same verbatim compute_term_spans computation.
                    # Revision-history and import-diff render call sites
                    # receive no highlight parameters (markup-identical, SC-9).
                    view_highlight_spans = None
                    if search_term:
                        if st.session_state.search_mode == "FTS":
                            view_highlight_spans = [compute_fts_spans(line, search_term) for line in mdf_lines]
                        else:
                            page_terms = getattr(search_result, "matched_terms", None)
                            record_terms = sorted(page_terms.get(record_id, ())) if page_terms else []
                            if record_terms:
                                view_highlight_spans = [compute_term_spans(line, record_terms) for line in mdf_lines]

                    render_mdf_block(
                        mdf_data,
                        diagnostics=diagnostics,
                        key=f"render_{record_id}",
                        highlight_spans=view_highlight_spans,
                    )

                    # Action Toolbar
                    toolbar_cols = [1, 1]
                    if user_role in ["editor", "admin"] and not st.session_state.global_edit_mode:
                        toolbar_cols.append(1)
                        toolbar_cols.append(1)

                    toolbar = st.columns(toolbar_cols)

                    in_selection = record_id in [r["id"] for r in st.session_state.selection]
                    selection_label = "Remove from Selection" if in_selection else "Add to Selection"
                    selection_icon = "🧺" if not in_selection else "❌"

                    if toolbar[0].button(
                        selection_label, use_container_width=True, icon=selection_icon, key=f"selection_{record_id}"
                    ):
                        if not in_selection:
                            st.session_state.selection.append(record)
                            st.toast(f"Added Record #{record_id} to selection")
                        else:
                            st.session_state.selection = [r for r in st.session_state.selection if r["id"] != record_id]
                            st.toast(f"Removed Record #{record_id} from selection")

                        if user_email:
                            selection_ids = [r["id"] for r in st.session_state.selection]
                            PreferenceService.set_preference(
                                user_email, "global", "selection_contents", json.dumps(selection_ids)
                            )
                        st.rerun()

                    if user_role in ["editor", "admin"]:
                        if st.session_state.confirm_delete_id == record_id:
                            st.warning("Confirm deletion?")
                            c_del1, c_del2, _ = st.columns([1, 1, 4])
                            if c_del1.button(
                                "Confirm", key=f"confirm_del_{record_id}", type="primary", use_container_width=True
                            ):
                                if LinguisticService.soft_delete_record(record_id, user_email):
                                    st.success(f"Record #{record_id} deleted.")
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                                else:
                                    handle_ui_error(
                                        Exception("Delete failed"),
                                        f"Failed to delete Record #{record_id}.",
                                        logger_name="snea.pages.records",
                                    )
                            if c_del2.button("Cancel", key=f"cancel_del_{record_id}", use_container_width=True):
                                st.session_state.confirm_delete_id = None
                                st.rerun()
                        else:
                            if toolbar[1].button("Delete", use_container_width=True, icon="🗑️", key=f"del_{record_id}"):
                                st.session_state.confirm_delete_id = record_id
                                st.rerun()

                        if not st.session_state.global_edit_mode:
                            # Disable edit if locked
                            if record.get("is_locked"):
                                toolbar[2].button(
                                    "Edit",
                                    use_container_width=True,
                                    icon="📝",
                                    key=f"edit_btn_{record_id}",
                                    disabled=True,
                                    help="Record is locked.",
                                )
                            else:
                                if toolbar[2].button(
                                    "Edit", use_container_width=True, icon="📝", key=f"edit_btn_{record_id}"
                                ):
                                    st.session_state.local_edits.add(record_id)
                                    st.rerun()

                            # Inline lock/unlock toggle
                            if record.get("is_locked"):
                                if toolbar[3].button(
                                    "Unlock",
                                    icon="🔓",
                                    use_container_width=True,
                                    key=f"unlock_btn_{record_id}",
                                    help=f"Unlock (locked by {record.get('locked_by')})",
                                ):
                                    if LinguisticService.unlock_record(record_id, user_email):
                                        st.success(f"Record #{record_id} unlocked.")
                                        st.rerun()
                            else:
                                if toolbar[3].button(
                                    "Lock",
                                    icon="🔒",
                                    use_container_width=True,
                                    key=f"lock_btn_{record_id}",
                                    help="Lock record",
                                ):
                                    if LinguisticService.lock_record(record_id, user_email):
                                        st.success(f"Record #{record_id} locked.")
                                        st.rerun()

                # Revision History
                with st.expander("Revision History"):
                    history = LinguisticService.get_edit_history(record_id)
                    if not history:
                        st.info("No revision history available.")
                    else:
                        is_editing = st.session_state.global_edit_mode or record_id in st.session_state.local_edits
                        for entry in history:
                            st.markdown(f"**v{entry['version']}** - {entry['user_email']} at {entry['timestamp']}")
                            st.caption(f"Summary: {entry['change_summary']}")
                            if entry.get("current_data"):
                                hist_diags, _ = compute_mdf_line_diffs(entry["current_data"], mdf_data)
                                render_mdf_block(
                                    entry["current_data"], diagnostics=hist_diags, key=f"hist_{record_id}_{entry['id']}"
                                )
                            if is_editing and entry.get("current_data"):
                                if st.button("↩ Rollback to this version", key=f"rollback_{record_id}_{entry['id']}"):
                                    st.session_state.pending_edits[record_id] = entry["current_data"]
                                    st.session_state.local_edits.add(record_id)
                                    st.rerun()
                            if entry != history[-1]:
                                st.divider()


if __name__ == "__main__":
    records()
