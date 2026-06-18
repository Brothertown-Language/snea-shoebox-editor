# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""Tests for Phase C (C-1 through C-5): Upload MDF page."""

import unittest
from datetime import UTC
from pathlib import Path
from unittest.mock import MagicMock, patch

SAMPLE_FILE = Path("src/seed_data/natick_sample_100.txt")


class TestUploadMdfRoleGuard(unittest.TestCase):
    """C-2: Only editor/admin may access the page."""

    @patch("src.database.connection.get_session")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {"user_role": "viewer"})
    def test_viewer_blocked(self, mock_error, _mock_session):
        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()
        mock_error.assert_called_once()
        self.assertIn("permission", mock_error.call_args[0][0].lower())

    @patch("src.database.connection.get_session")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {})
    def test_no_role_blocked(self, mock_error, _mock_session):
        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()
        mock_error.assert_called_once()

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    def test_editor_allowed(self, _fu, _sb, mock_sidebar, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()
        # Header is in sidebar now, or replaced by file_uploader label
        mock_sidebar.__enter__.assert_called()

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "admin"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    def test_admin_allowed(self, _fu, _sb, mock_sidebar, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()
        mock_sidebar.__enter__.assert_called()


class TestUploadMdfSourceSelector(unittest.TestCase):
    """C-4 / C-4a: Source selector with create-new option."""

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.sidebar")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.selectbox")
    def test_source_options_include_create_new(self, mock_selectbox, _fu, mock_sidebar, mock_session):
        src1 = MagicMock()
        src1.name = "Alpha"
        src1.id = 1
        src2 = MagicMock()
        src2.name = "Beta"
        src2.id = 2
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = [src1, src2]
        mock_session.return_value = mock_sess
        mock_selectbox.return_value = "Alpha"

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        options = mock_selectbox.call_args[0][1]
        self.assertEqual(options, ["Select a source...", "+ Add new source…", "Alpha", "Beta"])

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.sidebar")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.selectbox", return_value="+ Add new source…")
    @patch("streamlit.markdown")
    @patch("streamlit.text_input", side_effect=["New Source", "A description"])
    @patch("streamlit.button", return_value=False)
    def test_create_new_source_shows_inputs(self, _btn, mock_input, mock_md, _sb, _fu, mock_sidebar, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_md.assert_any_call("#### Create a new source")
        self.assertEqual(mock_input.call_count, 2)


class TestUploadMdfFileUploader(unittest.TestCase):
    """C-3: File uploader accepts .txt/.mdf and shows preview."""

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader")
    def test_file_uploader_accepts_txt_mdf(self, mock_uploader, _sb, _title, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        mock_uploader.return_value = None

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        kwargs = mock_uploader.call_args
        self.assertNotIn("type", kwargs[1])


class TestUploadMdfParseSummary(unittest.TestCase):
    """C-5: Parse upload and display summary table."""

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_parse_and_display(
        self, mock_uploader, mock_expander, mock_success, mock_dataframe, _sb, _title, mock_parse, mock_session
    ):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"\\lx word1\n\\ps n\n\\ge thing"
        mock_file.name = "test.txt"
        mock_uploader.return_value = mock_file

        mock_expander_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_parse.return_value = [
            {"lx": "word1", "ps": "n", "ge": "thing"},
        ]

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_success.assert_called_once()
        self.assertIn("1", mock_success.call_args[0][0])
        mock_dataframe.assert_called_once()
        rows = mock_dataframe.call_args[0][0]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["lx"], "word1")

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.error")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_parse_error_displayed(
        self, mock_uploader, mock_expander, mock_error, _sb, _title, mock_parse, mock_session
    ):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"no valid entries"
        mock_file.name = "bad.txt"
        mock_uploader.return_value = mock_file

        mock_expander_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_parse.side_effect = ValueError("No valid MDF entries found")

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_error.assert_called()
        self.assertIn("No valid", mock_error.call_args[0][0])

    @patch("src.database.connection.get_session")
    @patch("streamlit.session_state", {"user_role": "admin"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_sample_file_parse(
        self, mock_uploader, mock_expander, mock_success, mock_dataframe, _sb, _title, mock_session
    ):
        """Integration-style test using the real sample file content."""
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        if not SAMPLE_FILE.exists():
            self.skipTest("Sample file not available")

        content = SAMPLE_FILE.read_text(encoding="utf-8")
        mock_file = MagicMock()
        mock_file.getvalue.return_value = content.encode("utf-8")
        mock_file.name = "natick_sample_100.txt"
        mock_uploader.return_value = mock_file

        mock_expander_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_success.assert_called_once()
        rows = mock_dataframe.call_args[0][0]
        self.assertIn(str(len(rows)), mock_success.call_args[0][0])
        self.assertEqual(len(rows), 150)


class TestStageAndMatch(unittest.TestCase):
    """C-6: Stage & Match button calls stage_entries then suggest_matches."""

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.suggest_matches")
    @patch("src.services.upload_service.UploadService.stage_entries")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch(
        "streamlit.session_state",
        {
            "user_role": "editor",
            "user_email": "test@example.com",
            "staging_in_progress": True,
            "_staging_progress_value": 0.0,
            "pending_upload_content": "\\lx word\n\\ps n\n\\ge thing",
            "pending_upload_name": "test.txt",
            "pending_upload_file_id": "file-id-1",
            "upload_active_source_name": "TestSource",
        },
    )
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.warning")
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    @patch("streamlit.progress")
    @patch("streamlit.status")
    @patch("streamlit.rerun")
    @patch("streamlit.switch_page")
    def test_stage_and_match_called(
        self,
        _switch_page,
        _rerun,
        mock_status,
        mock_progress,
        _info,
        _subheader,
        _divider,
        _warning,
        mock_button,
        mock_uploader,
        mock_expander,
        mock_success,
        _df,
        _sb,
        _title,
        mock_list_batches,
        mock_parse,
        mock_stage,
        mock_suggest,
        mock_session,
    ):
        mock_status_ctx = MagicMock()
        mock_status.return_value.__enter__ = MagicMock(return_value=mock_status_ctx)
        mock_status.return_value.__exit__ = MagicMock(return_value=False)
        mock_sess = MagicMock()
        src = MagicMock()
        src.name = "TestSource"
        src.id = 1
        mock_sess.query.return_value.order_by.return_value.all.return_value = [src]
        mock_session.return_value = mock_sess

        mock_uploader.return_value = None

        mock_expander_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_progress.return_value = MagicMock()

        mock_parse.return_value = [{"lx": "word", "ps": "n", "ge": "thing"}]
        mock_stage.return_value = "batch-uuid-1234"
        mock_suggest.return_value = [{"queue_id": 1, "lx": "word", "suggested_record_id": 42, "match_type": "exact"}]
        mock_list_batches.return_value = []

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_stage.assert_called_once_with(
            user_email="test@example.com",
            source_id=1,
            entries=[{"lx": "word", "ps": "n", "ge": "thing"}],
            filename="test.txt",
        )
        mock_suggest.assert_called_once()
        self.assertEqual(mock_suggest.call_args[0][0], "batch-uuid-1234")

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="+ Add new source…")
    @patch("streamlit.file_uploader")
    @patch("streamlit.warning")
    @patch("streamlit.markdown")
    @patch("streamlit.text_input", side_effect=["", ""])
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_stage_blocked_without_source(
        self,
        _info,
        _subheader,
        _divider,
        _btn,
        _ti,
        _md,
        mock_warning,
        mock_uploader,
        _sb,
        _title,
        mock_list_batches,
        mock_parse,
        mock_session,
    ):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"\\lx word\n\\ps n\n\\ge thing"
        mock_file.name = "test.txt"
        mock_uploader.return_value = mock_file

        mock_parse.return_value = [{"lx": "word", "ps": "n", "ge": "thing"}]
        mock_list_batches.return_value = []

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        mock_warning.assert_any_call("Select a source collection before staging.")


class TestPendingBatchSelector(unittest.TestCase):
    """C-6a: Pending upload batches shown inline on main upload view."""

    @patch("src.services.identity_service.IdentityService.get_github_username", return_value="testuser")
    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.subheader")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.markdown")
    @patch("streamlit.container")
    @patch("streamlit.divider")
    @patch("streamlit.info")
    def test_batch_selector_displayed(
        self,
        _info,
        _divider,
        mock_container,
        _md,
        _btn,
        mock_columns,
        mock_subheader,
        _fu,
        _sb,
        _title,
        mock_list_batches,
        mock_session,
        _mock_github,
    ):
        from datetime import datetime

        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        mock_list_batches.return_value = [
            {
                "batch_id": "abc-123",
                "source_id": 1,
                "source_name": "Natick",
                "filename": "natick.txt",
                "entry_count": 50,
                "uploaded_at": datetime(2026, 2, 8, 14, 52, tzinfo=UTC),
            }
        ]

        col_mock = MagicMock()
        col_mock.__enter__ = MagicMock(return_value=col_mock)
        col_mock.__exit__ = MagicMock(return_value=False)
        mock_columns.return_value = [col_mock, col_mock, col_mock, col_mock]

        container_mock = MagicMock()
        container_mock.__enter__ = MagicMock(return_value=container_mock)
        container_mock.__exit__ = MagicMock(return_value=False)
        mock_container.return_value = container_mock

        from src.frontend.pages.upload_mdf import upload_mdf

        with (
            patch("src.services.upload_service.UploadService.get_pending_batch_mdf") as mock_get_mdf,
            patch("streamlit.download_button") as mock_download_btn,
        ):
            mock_get_mdf.return_value = "\\lx test\n\\ge gloss"
            upload_mdf()

            # Verify list_pending_batches was called and subheader shows count
            mock_list_batches.assert_called_once_with("test@example.com")
            mock_subheader.assert_any_call("1 Pending Batch")

            # Verify columns were created for Review, Download, Discard (4 columns total)
            mock_columns.assert_any_call([4, 1, 1, 1])

            # Verify download button was rendered with the improved filename format
            mock_download_btn.assert_called_once()
            self.assertEqual(mock_download_btn.call_args[1]["data"], "\\lx test\n\\ge gloss")
            self.assertEqual(mock_download_btn.call_args[1]["mime"], "text/plain")
            # Format: pending_<Source>_<GitHubUsername>_<YYYY-MM-DD>_<SSSSS>.txt
            # 14:52:00 = 14*3600 + 52*60 = 50400 + 3120 = 53520
            self.assertEqual(
                mock_download_btn.call_args[1]["file_name"], "pending_Natick_testuser_2026-02-08_53520.txt"
            )

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.header")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.info")
    @patch("streamlit.divider")
    def test_no_batches_shows_upload_info(
        self, _divider, mock_info, _btn, _fu, _sb, _title, mock_list_batches, mock_session
    ):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        mock_list_batches.return_value = []

        from src.frontend.pages.upload_mdf import upload_mdf

        upload_mdf()

        # With no batches and no file, should show the upload prompt
        mock_info.assert_any_call("Upload an MDF file using the sidebar to get started.")


class TestReMatchButton(unittest.TestCase):
    """C-6b: Re-Match button calls rematch_batch (now in dedicated review view)."""

    @patch("src.database.connection.get_session")
    @patch("src.services.upload_service.UploadService.rematch_batch")
    @patch(
        "streamlit.session_state",
        {
            "user_role": "editor",
            "user_email": "test@example.com",
            "review_batch_id": "abc-123",
            "review_current_page": 1,
            "review_page_size": 10,
            "review_filter_status": "All Records",
            "review_bulk_in_progress": True,
            "review_bulk_action": "rematch",
        },
    )
    @patch("streamlit.header")
    @patch("streamlit.sidebar")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.success")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox", return_value="All Records")
    @patch("streamlit.code")
    @patch("streamlit.container")
    @patch("streamlit.status")
    def test_rematch_calls_service(
        self,
        mock_status,
        mock_container,
        _code,
        _selectbox,
        _md,
        mock_info,
        _subheader,
        mock_success,
        mock_button,
        mock_columns,
        mock_sidebar,
        _title,
        mock_rematch,
        mock_session,
    ):
        mock_sess = MagicMock()
        # Non-empty batch so _render_review_table doesn't trigger early rerun
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.lx = "word"
        mock_row.status = "pending"
        mock_row.suggested_record_id = None
        mock_row.match_type = None
        mock_row.batch_id = "abc-123"
        mock_row.source_id = 1
        mock_row.mdf_data = r"\lx word"
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_row
        ]
        mock_sess.query.return_value.filter_by.return_value.count.return_value = 1
        mock_sess.query.return_value.filter_by.return_value.filter.return_value.count.return_value = 1
        mock_sess.query.return_value.first.return_value = MagicMock(id=2)
        mock_sess.get.return_value = MagicMock(name="TestSource")
        # Support both plain call and context-manager usage of get_session()
        cm_sess = MagicMock()
        cm_sess.query.return_value.filter_by.return_value.count.return_value = 0
        mock_sess.__enter__ = MagicMock(return_value=cm_sess)
        mock_sess.__exit__ = MagicMock(return_value=False)
        mock_session.return_value = mock_sess

        mock_sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_sidebar.__exit__ = MagicMock(return_value=False)

        status_ctx = MagicMock()
        status_ctx.__enter__ = MagicMock(return_value=status_ctx)
        status_ctx.__exit__ = MagicMock(return_value=False)
        mock_status.return_value = status_ctx

        mock_rematch.return_value = [{"queue_id": 1, "lx": "word", "suggested_record_id": 10, "match_type": "exact"}]

        def _make_col():
            c = MagicMock()
            c.__enter__ = MagicMock(return_value=c)
            c.__exit__ = MagicMock(return_value=False)
            return c

        def _cols_effect(arg, **kw):
            n = arg if isinstance(arg, int) else len(arg)
            return [_make_col() for _ in range(n)]

        mock_columns.side_effect = _cols_effect

        # Use label-based side_effect: only "Re-Match" returns True
        mock_button.side_effect = lambda label, **kw: label == "Re-Match"

        from src.frontend.pages.upload_mdf import upload_mdf

        with patch("src.frontend.ui_utils.handle_ui_error", side_effect=lambda e, *a, **kw: (_ for _ in ()).throw(e)):
            upload_mdf()

        mock_rematch.assert_called_once()
        self.assertEqual(mock_rematch.call_args[0][0], "abc-123")


if __name__ == "__main__":
    unittest.main()
