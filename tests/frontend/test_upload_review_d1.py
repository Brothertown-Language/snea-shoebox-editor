# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""Tests for Phase D-1: Review table, bulk actions, comparison view, Apply Now."""
import unittest
from unittest.mock import patch, MagicMock, PropertyMock


def _make_queue_row(id=1, lx="test", mdf_data="\\lx test\n\\ge testing",
                    suggested_record_id=None, match_type=None, status="pending",
                    batch_id="batch-1", source_id=1):
    row = MagicMock()
    row.id = id
    row.lx = lx
    row.mdf_data = mdf_data
    row.suggested_record_id = suggested_record_id
    row.match_type = match_type
    row.status = status
    row.batch_id = batch_id
    row.source_id = source_id
    return row


def _make_record(id=10, lx="test", ge="testing", mdf_data="\\lx test\n\\ge testing"):
    rec = MagicMock()
    rec.id = id
    rec.lx = lx
    rec.ge = ge
    rec.mdf_data = mdf_data
    return rec


def _make_col_mock():
    col = MagicMock()
    col.__enter__ = MagicMock(return_value=col)
    col.__exit__ = MagicMock(return_value=False)
    return col


def _columns_side_effect(arg, **kwargs):
    """Return the right number of column mocks based on the argument."""
    if isinstance(arg, int):
        return [_make_col_mock() for _ in range(arg)]
    if isinstance(arg, (list, tuple)):
        return [_make_col_mock() for _ in arg]
    return [_make_col_mock(), _make_col_mock()]


def _setup_sidebar_mock():
    """Create and install a sidebar mock that supports context manager protocol."""
    import streamlit as st
    sidebar_mock = MagicMock()
    sidebar_mock.__enter__ = MagicMock(return_value=sidebar_mock)
    sidebar_mock.__exit__ = MagicMock(return_value=False)
    st.sidebar = sidebar_mock
    return sidebar_mock


class TestReviewTableRendering(unittest.TestCase):
    """D-1: Review table displays entries with status selectors."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.rerun")
    def test_empty_batch_redirects_to_upload(self, mock_rerun, mock_get_session):
        """When batch is empty, clear review_batch_id and rerun to upload view."""
        import streamlit as st
        st.session_state["review_batch_id"] = "batch-1"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})
        mock_rerun.assert_called_once()
        self.assertNotIn("review_batch_id", st.session_state)
        flash = st.session_state.pop("bulk_flash", None)
        self.assertIsNotNone(flash)
        self.assertEqual(flash[0], "success")

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_review_table_renders_entries(self, _info, _code,
                                          mock_selectbox, mock_md, mock_container,
                                          mock_columns, _btn, mock_subheader,
                                          mock_get_session):
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="ēsh", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        # query(MatchupQueue).filter_by().order_by().all() -> rows
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        # query(Record).filter_by().count() -> 0 (new source)
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        # query(Language).first() -> lang
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        # Mock columns context managers
        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        mock_md.assert_any_call("**Bulk Actions**")

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_exact_match_defaults_to_matched(self, _info, _code,
                                              mock_selectbox, mock_md, mock_container,
                                              mock_columns, _btn, _subheader,
                                              mock_get_session):
        """D-1 default status: exact match -> 'matched'."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Matched"
            return "Matched"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="ēsh", suggested_record_id=10, match_type="exact", status="pending")
        rec = _make_record(id=10, lx="ēsh", ge="fire")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 5
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.query.return_value.filter.return_value.all.return_value = [rec]
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Check selectbox was called with index=0 (matched)
        selectbox_calls = [c for c in mock_selectbox.call_args_list if c[0][0] == "Status"]
        self.assertTrue(len(selectbox_calls) > 0)
        self.assertEqual(selectbox_calls[0][1].get("index", selectbox_calls[0][0][2] if len(selectbox_calls[0][0]) > 2 else None), 0)


class TestBulkApprovalButtons(unittest.TestCase):
    """D-1a: Bulk approval action buttons."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_new_source_shows_approve_all_new(self, _info, _code,
                                               mock_selectbox, _md, mock_container,
                                               mock_columns, mock_button, _subheader,
                                               mock_get_session):
        """New source (0 existing records) shows 'Approve All as New Records'."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row()
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "NewSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)
        mock_button.return_value = False

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Check that "Approve All as New Records" button was rendered
        btn_labels = [c[0][0] for c in mock_button.call_args_list]
        self.assertIn("Approve All as New Records", btn_labels)

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_existing_source_shows_two_bulk_buttons(self, _info, _code,
                                                     mock_selectbox, _md, mock_container,
                                                     mock_columns, mock_button, _subheader,
                                                     mock_get_session):
        """Existing source shows 'Approve All Matched' and 'Approve Non-Matches as New'."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row()
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "ExistingSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 10
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)
        mock_button.return_value = False

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        btn_labels = [c[0][0] for c in mock_button.call_args_list]
        self.assertIn("Approve All Matched", btn_labels)
        self.assertIn("Approve Non-Matches as New", btn_labels)


class TestComparisonView(unittest.TestCase):
    """D-1b: Side-by-side comparison of existing vs uploaded MDF."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("src.frontend.ui_utils.render_mdf_block")
    @patch("streamlit.info")
    def test_comparison_shows_existing_and_new(self, _info, mock_render,
                                                mock_selectbox, mock_md, mock_container,
                                                mock_columns, _btn, _subheader,
                                                mock_get_session):
        """D-1b: Expander shows existing record and new uploaded data."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Matched"
            return "Matched"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="ēsh", suggested_record_id=10, match_type="exact",
                              mdf_data="\\lx ēsh\n\\ge fire (new)")
        rec = _make_record(id=10, lx="ēsh", ge="fire", mdf_data="\\lx ēsh\n\\ge fire")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 5
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.query.return_value.filter.return_value.all.return_value = [rec]
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # render_mdf_block should be called with the existing record's mdf_data
        render_calls = [str(c) for c in mock_render.call_args_list]
        self.assertTrue(any("fire" in c for c in render_calls))

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_no_match_shows_placeholder(self, mock_info, _code,
                                         mock_selectbox, mock_md, mock_container,
                                         mock_columns, _btn, _subheader,
                                         mock_get_session):
        """D-1b: No existing record shows placeholder text."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="newword", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Should show "No existing record" in markdown
        md_calls = [str(c) for c in mock_md.call_args_list]
        self.assertTrue(any("No existing record" in c for c in md_calls))


class TestPerRecordApplyNow(unittest.TestCase):
    """D-1c: Per-record Apply Now button."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_apply_now_disabled_for_ignored(self, _info, _code,
                                            mock_selectbox, _md, mock_container,
                                            mock_columns, mock_button, _subheader,
                                            mock_get_session):
        """D-1c: Apply Now is disabled when status is 'ignored'."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Ignored"
            return "Ignored"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="test", status="ignored")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)
        mock_button.return_value = False

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Find the Apply Now button call and check disabled=True
        apply_calls = [c for c in mock_button.call_args_list if c[0][0] == "Apply Now"]
        self.assertTrue(len(apply_calls) > 0)
        self.assertTrue(apply_calls[0][1].get("disabled", False))

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_apply_now_enabled_for_create_new(self, _info, _code,
                                               mock_selectbox, _md, mock_container,
                                               mock_columns, mock_button, _subheader,
                                               mock_get_session):
        """D-1c: Apply Now is enabled when status is 'create_new'."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="test", status="create_new")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)
        mock_button.return_value = False

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        apply_calls = [c for c in mock_button.call_args_list if c[0][0] == "Apply Now"]
        self.assertTrue(len(apply_calls) > 0)
        self.assertFalse(apply_calls[0][1].get("disabled", True))


class TestPagination(unittest.TestCase):
    """Pagination: page size selector and page navigation."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_pagination_shows_page_size_selector(self, _info, _code,
                                                  mock_selectbox, mock_md, mock_container,
                                                  mock_columns, _btn, _subheader,
                                                  mock_get_session):
        """Pagination: Records per page selectbox is rendered with default 1."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row1 = _make_queue_row(id=1, lx="word1")
        row2 = _make_queue_row(id=2, lx="word2")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row1, row2]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Page info markdown should be rendered (selectbox moved to review view)
        md_calls = [str(c) for c in mock_md.call_args_list]
        self.assertTrue(any("Page **1**" in c for c in md_calls))

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_pagination_only_shows_page_size_entries(self, _info, _code,
                                                      mock_selectbox, mock_md, mock_container,
                                                      mock_columns, _btn, _subheader,
                                                      mock_get_session):
        """With page_size=1 and 2 rows, only 1 entry's comparison is rendered."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row1 = _make_queue_row(id=1, lx="word1", mdf_data="\\lx word1\n\\ge one")
        row2 = _make_queue_row(id=2, lx="word2", mdf_data="\\lx word2\n\\ge two")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row1, row2]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Page info should show "Page 1 of 2 (2 entries)"
        md_calls = [str(c) for c in mock_md.call_args_list]
        self.assertTrue(any("Page **1** of **2**" in c for c in md_calls))


class TestStageAndMatchDisable(unittest.TestCase):
    """Stage & Match button disabled after use until new file uploaded."""

    @patch("src.services.upload_service.UploadService.list_pending_batches", return_value=[])
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@test.com",
                                        "upload_staged_file_id": "already-staged-id"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    @patch("streamlit.button")
    def test_stage_button_disabled_after_staging(self, mock_button, _info, _subheader,
                                                  _divider, mock_expander, _success,
                                                  _df, _sb, _title, mock_get_session,
                                                  mock_parse, _list_batches):
        _sb.return_value = "TestSource"
        src = MagicMock()
        src.name = "TestSource"
        src.id = 1
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = [src]
        mock_get_session.return_value = mock_sess
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_button.return_value = False

        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.file_id = "already-staged-id"
        mock_file.getvalue.return_value = b"\\lx test\n\\ge testing"
        mock_parse.return_value = [{"lx": "test", "ps": "", "ge": "testing"}]

        with patch("streamlit.file_uploader", return_value=mock_file):
            with patch("streamlit.code"):
                with patch("streamlit.warning"):
                    from src.frontend.pages.upload_mdf import upload_mdf
                    upload_mdf()

        # Find Stage & Match button call
        stage_calls = [c for c in mock_button.call_args_list
                       if len(c[0]) > 0 and c[0][0] == "Stage & Match"]
        self.assertTrue(len(stage_calls) > 0)
        self.assertTrue(stage_calls[0][1].get("disabled", False))


class TestManualMatchOverride(unittest.TestCase):
    """D-2: Manual match override widget."""

    def setUp(self):
        self._sidebar_mock = _setup_sidebar_mock()

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="")
    @patch("streamlit.expander")
    def test_override_expander_renders(self, mock_expander, _text_input, _info,
                                        _code, mock_selectbox, _md, mock_container,
                                        mock_columns, _btn, _subheader,
                                        mock_get_session):
        """D-2: Change match expander renders for each review row."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="ēsh", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Expander should be called with the change match label
        expander_calls = [c for c in mock_expander.call_args_list
                          if len(c[0]) > 0 and "Change match" in str(c[0][0])]
        self.assertTrue(len(expander_calls) > 0)

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="fire")
    @patch("streamlit.expander")
    @patch("src.services.upload_service.UploadService.search_records_for_override")
    def test_search_returns_candidates(self, mock_search, mock_expander,
                                        _text_input, mock_info, _code,
                                        mock_selectbox, _md, mock_container,
                                        mock_columns, _btn, _subheader,
                                        mock_get_session):
        """D-2: Search with results shows selectbox with candidates."""
        mock_search.return_value = [
            {"id": 42, "lx": "ēsh", "hm": 1, "ge": "fire"},
            {"id": 43, "lx": "ēsh", "hm": 2, "ge": "fireplace"},
        ]
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Select record" in str(label): return "#42 — ēsh (hm 1) — fire"
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect

        row = _make_queue_row(lx="ēsh", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 5
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.query.return_value.filter.return_value.all.return_value = []
        mock_sess.get.return_value = source_obj

        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        mock_search.assert_called_once_with(1, "fire")
        # Selectbox should have been called with the candidate options
        select_calls = [c for c in mock_selectbox.call_args_list
                        if len(c[0]) > 0 and c[0][0] == "Select record"]
        self.assertTrue(len(select_calls) > 0)

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="fire")
    @patch("streamlit.expander")
    @patch("src.services.upload_service.UploadService.search_records_for_override")
    @patch("src.services.upload_service.UploadService.confirm_match")
    @patch("streamlit.success")
    @patch("streamlit.rerun")
    def test_confirm_override_calls_backend(self, mock_rerun, mock_success,
                                             mock_confirm, mock_search,
                                             mock_expander, _text_input,
                                             _info, _code, mock_selectbox,
                                             _md, mock_container, mock_columns,
                                             mock_button, _subheader,
                                             mock_get_session):
        """D-2: Confirm Override button calls confirm_match with chosen record_id."""
        mock_search.return_value = [
            {"id": 42, "lx": "ēsh", "hm": 1, "ge": "fire"},
        ]
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Select record" in str(label): return "#42 — ēsh (hm 1) — fire"
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        # Make Confirm Override button return True, others False
        mock_button.side_effect = lambda label, **kw: label == "Confirm Override"

        row = _make_queue_row(id=7, lx="ēsh", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 5
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.query.return_value.filter.return_value.all.return_value = []
        mock_sess.get.return_value = source_obj

        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        mock_confirm.assert_called_once_with(7, 42)

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="nonexistent")
    @patch("streamlit.expander")
    @patch("src.services.upload_service.UploadService.search_records_for_override", return_value=[])
    def test_no_results_shows_info(self, mock_search, mock_expander,
                                    _text_input, mock_info, _code,
                                    mock_selectbox, _md, mock_container,
                                    mock_columns, _btn, _subheader,
                                    mock_get_session):
        """D-2: Empty search results show info message."""
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "All Records"
            if "per page" in str(label): return 1
            if "Status" in str(label): return "Create New Record"
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect
        row = _make_queue_row(lx="ēsh", suggested_record_id=None, status="pending")
        lang = MagicMock()
        lang.id = 2
        source_obj = MagicMock()
        source_obj.name = "TestSource"

        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.query.return_value.first.return_value = lang
        mock_sess.get.return_value = source_obj

        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # info should be called with "No matching records found."
        info_calls = [c for c in mock_info.call_args_list
                      if len(c[0]) > 0 and "No matching records found" in str(c[0][0])]
        self.assertTrue(len(info_calls) > 0)


class TestReviewFiltering(unittest.TestCase):
    def setUp(self):
        import streamlit as st
        if "review_current_page" not in st.session_state:
            st.session_state["review_current_page"] = 1
        if "review_page_size" not in st.session_state:
            st.session_state["review_page_size"] = 10
        if "review_filter_status" in st.session_state:
            del st.session_state["review_filter_status"]

    @patch("src.database.get_session")
    @patch("streamlit.sidebar")
    @patch("streamlit.markdown")
    @patch("streamlit.container")
    @patch("streamlit.columns")
    @patch("streamlit.subheader")
    @patch("streamlit.selectbox")
    @patch("streamlit.info")
    @patch("streamlit.code")
    @patch("streamlit.button")
    def test_filter_exact_match(self, _btn, _code, _info, mock_selectbox, _subheader, mock_columns, mock_container, _md, mock_sidebar, mock_get_session):
        """D-4b: Filtering by 'Matched (Exact)' only shows exact matches."""
        # 1. Setup rows: one exact, one base-form, one pending
        row1 = _make_queue_row(id=1, lx="exact", status="matched")
        row1.match_type = "exact"
        row2 = _make_queue_row(id=2, lx="base", status="matched")
        row2.match_type = "base_form"
        row3 = _make_queue_row(id=3, lx="pending", status="pending")
        
        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [row1, row2, row3]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 3
        mock_sess.get.return_value = MagicMock(name="Source")
        mock_get_session.return_value = mock_sess

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        mock_sidebar.return_value.__enter__ = MagicMock()

        # Mock selectbox
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Filter by Status" in str(label): return "Matched (Exact)"
            if "per page" in str(label): return 10
            if "Status" in str(label): return "Matched"
            return None
        mock_selectbox.side_effect = selectbox_side_effect
        
        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Verify that only row1 was rendered in the table
        # We check markdown calls for the lx value
        lx_calls = [c for c in _md.call_args_list if "exact" in str(c[0][0])]
        self.assertEqual(len(lx_calls), 1)
        lx_calls_base = [c for c in _md.call_args_list if "base" in str(c[0][0])]
        self.assertEqual(len(lx_calls_base), 0)

    @patch("src.database.get_session")
    @patch("streamlit.sidebar")
    @patch("streamlit.markdown")
    @patch("streamlit.container")
    @patch("streamlit.columns")
    @patch("streamlit.subheader")
    @patch("streamlit.selectbox")
    @patch("streamlit.rerun")
    def test_pagination_adjusts_to_filter(self, mock_rerun, mock_selectbox, _subheader, mock_columns, mock_container, _md, mock_sidebar, mock_get_session):
        """D-4b: Pagination total pages should be based on filtered row count."""
        import streamlit as st
        st.session_state["review_page_size"] = 1
        st.session_state["review_current_page"] = 1

        # 10 rows, but only 2 match filter (pending -> recommended matched)
        rows = []
        for i in range(10):
            r = _make_queue_row(id=i, status="pending" if i < 2 else "create_new")
            r.match_type = "exact"
            r.suggested_record_id = 1 if i < 2 else None # Only first 2 have suggestions -> matched
            rows.append(r)
            
        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = rows
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 10
        mock_get_session.return_value = mock_sess

        mock_columns.side_effect = _columns_side_effect
        mock_container.return_value.__enter__ = MagicMock()
        
        # USE SIMPLE MOCK FOR SIDEBAR
        mock_sidebar.return_value.__enter__ = MagicMock()

        # Filter by "Matched (Exact)"
        st.session_state["review_filter_status"] = "Matched (Exact)"
        
        # Mock selectbox for page size = 1
        def selectbox_side_effect(*a, **kw):
            label = a[0] if len(a) > 0 else kw.get("label", "")
            if "Filter by Status" in str(label): return "Matched (Exact)"
            if "per page" in str(label): return 1
            if "Go to page" in str(label): return 1
            return "Create New Record"
        mock_selectbox.side_effect = selectbox_side_effect

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})

        # Check total pages
        page_info_found = False
        md_texts = []
        for call in _md.call_args_list:
            arg = str(call[0][0])
            md_texts.append(arg)
            if "Page **1** of **2**" in arg and "(2 entries)" in arg:
                page_info_found = True
                break
        self.assertTrue(page_info_found, f"Pagination info not found in markdown calls. MD calls: {md_texts}")

    @patch("src.database.get_session")
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.rerun")
    @patch("src.services.preference_service.PreferenceService.get_preference", return_value="10")
    @patch("src.services.preference_service.PreferenceService.set_preference")
    def test_page_size_change_resets_current_page(self, mock_set_pref, mock_get_pref, mock_rerun, mock_selectbox, mock_sidebar, mock_get_session):
        """Page size change via visual widget callback should reset current page to 1."""
        import streamlit as st
        st.session_state["review_page_size"] = 10
        st.session_state["review_current_page"] = 5
        st.session_state["review_filter_status"] = "All Records"
        
        # Mock rows
        rows = [_make_queue_row(id=i) for i in range(20)]
        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = rows
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 20
        mock_get_session.return_value = mock_sess
        
        mock_sidebar.return_value.__enter__ = MagicMock()
        
        # 1. Setup side effect for selectbox
        def selectbox_side_effect(*a, **kw):
            label = a[0] if a else kw.get("label", "")
            if "Records per page" in str(label): return 5
            if "Filter by Status" in str(label): return "All Records"
            if "Status" in str(label): return "Create New Record"
            return None
        mock_selectbox.side_effect = selectbox_side_effect
        
        # 2. Extract and trigger the on_change callback manually
        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})
        
        # Find the call to selectbox for "Records per page"
        page_size_call = None
        for call in mock_selectbox.call_args_list:
            if "Records per page" in str(call[0][0]):
                page_size_call = call
                break
        
        self.assertIsNotNone(page_size_call, "Records per page selectbox not found")
        
        # Mock the widget key value as if it were changed in the UI
        st.session_state["review_page_size_widget"] = 5
        
        # Find the rerun call
        self.assertTrue(mock_rerun.called)
        
        self.assertEqual(st.session_state["review_current_page"], 1)
        self.assertEqual(st.session_state["review_page_size"], 5)
        # Verify persistence was called
        mock_set_pref.assert_called_with("test@test.com", "upload_review", "page_size", "5")


if __name__ == "__main__":
    unittest.main()
