# Copyright (c) 2026 Brothertown Language
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
    @patch("streamlit.info")
    def test_empty_batch_shows_info(self, mock_info, mock_get_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
        mock_get_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import _render_review_table
        _render_review_table("batch-1", session_deps={"user_email": "test@test.com"})
        mock_info.assert_called_once()
        self.assertIn("No entries", mock_info.call_args[0][0])

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_review_table_renders_entries(self, _info, _code,
                                          mock_selectbox, mock_md, mock_container,
                                          mock_columns, _btn, mock_subheader,
                                          mock_get_session):
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

        mock_subheader.assert_any_call("Bulk Actions")

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "matched")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_exact_match_defaults_to_matched(self, _info, _code,
                                              mock_selectbox, mock_md, mock_container,
                                              mock_columns, _btn, _subheader,
                                              mock_get_session):
        """D-1 default status: exact match -> 'matched'."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_new_source_shows_approve_all_new(self, _info, _code,
                                               _selectbox, _md, mock_container,
                                               mock_columns, mock_button, _subheader,
                                               mock_get_session):
        """New source (0 existing records) shows 'Approve All as New Records'."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_existing_source_shows_two_bulk_buttons(self, _info, _code,
                                                     _selectbox, _md, mock_container,
                                                     mock_columns, mock_button, _subheader,
                                                     mock_get_session):
        """Existing source shows 'Approve All Matched' and 'Approve Non-Matches as New'."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "matched")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_comparison_shows_existing_and_new(self, _info, mock_code,
                                                _selectbox, mock_md, mock_container,
                                                mock_columns, _btn, _subheader,
                                                mock_get_session):
        """D-1b: Expander shows existing record and new uploaded data."""
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

        # Code should be called with the existing record's mdf_data
        code_calls = [str(c) for c in mock_code.call_args_list]
        self.assertTrue(any("fire" in c for c in code_calls))

    @patch("src.database.get_session")
    @patch("streamlit.subheader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_no_match_shows_placeholder(self, mock_info, _code,
                                         _selectbox, mock_md, mock_container,
                                         mock_columns, _btn, _subheader,
                                         mock_get_session):
        """D-1b: No existing record shows placeholder text."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "ignore")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_apply_now_disabled_for_ignore(self, _info, _code,
                                            _selectbox, _md, mock_container,
                                            mock_columns, mock_button, _subheader,
                                            mock_get_session):
        """D-1c: Apply Now is disabled when status is 'ignore'."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_apply_now_enabled_for_create_new(self, _info, _code,
                                               _selectbox, _md, mock_container,
                                               mock_columns, mock_button, _subheader,
                                               mock_get_session):
        """D-1c: Apply Now is enabled when status is 'create_new'."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_pagination_shows_page_size_selector(self, _info, _code,
                                                  mock_selectbox, mock_md, mock_container,
                                                  mock_columns, _btn, _subheader,
                                                  mock_get_session):
        """Pagination: Records per page selectbox is rendered with default 1."""
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    def test_pagination_only_shows_page_size_entries(self, _info, _code,
                                                      _selectbox, mock_md, mock_container,
                                                      mock_columns, _btn, _subheader,
                                                      mock_get_session):
        """With page_size=1 and 2 rows, only 1 entry's comparison is rendered."""
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
    @patch("streamlit.selectbox", return_value="TestSource")
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="")
    @patch("streamlit.expander")
    def test_override_expander_renders(self, mock_expander, _text_input, _info,
                                        _code, _selectbox, _md, mock_container,
                                        mock_columns, _btn, _subheader,
                                        mock_get_session):
        """D-2: Change match expander renders for each review row."""
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
        mock_selectbox.side_effect = lambda *a, **kw: (
            1 if "per page" in a[0]
            else "#42 — ēsh (hm 1) — fire" if "Select record" in a[0]
            else "create_new"
        )

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
        mock_selectbox.side_effect = lambda *a, **kw: (
            1 if "per page" in a[0]
            else "#42 — ēsh (hm 1) — fire" if "Select record" in a[0]
            else "create_new"
        )
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
    @patch("streamlit.selectbox", side_effect=lambda *a, **kw: 1 if "per page" in a[0] else "create_new")
    @patch("streamlit.code")
    @patch("streamlit.info")
    @patch("streamlit.text_input", return_value="nonexistent")
    @patch("streamlit.expander")
    @patch("src.services.upload_service.UploadService.search_records_for_override", return_value=[])
    def test_no_results_shows_info(self, mock_search, mock_expander,
                                    _text_input, mock_info, _code,
                                    _selectbox, _md, mock_container,
                                    mock_columns, _btn, _subheader,
                                    mock_get_session):
        """D-2: Empty search results show info message."""
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


if __name__ == "__main__":
    unittest.main()
