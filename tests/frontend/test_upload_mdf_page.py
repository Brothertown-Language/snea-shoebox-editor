# Copyright (c) 2026 Brothertown Language
"""Tests for Phase C (C-1 through C-5): Upload MDF page."""
import os
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

SAMPLE_FILE = Path("src/seed_data/natick_sample_100.txt")


class TestUploadMdfRoleGuard(unittest.TestCase):
    """C-2: Only editor/admin may access the page."""

    @patch("src.database.get_session")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {"user_role": "viewer"})
    def test_viewer_blocked(self, mock_error, _mock_session):
        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()
        mock_error.assert_called_once()
        self.assertIn("permission", mock_error.call_args[0][0].lower())

    @patch("src.database.get_session")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {})
    def test_no_role_blocked(self, mock_error, _mock_session):
        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()
        mock_error.assert_called_once()

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    def test_editor_allowed(self, _fu, _sb, mock_title, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()
        mock_title.assert_called_once_with("Upload MDF File")

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "admin"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    def test_admin_allowed(self, _fu, _sb, mock_title, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()
        mock_title.assert_called_once_with("Upload MDF File")


class TestUploadMdfSourceSelector(unittest.TestCase):
    """C-4 / C-4a: Source selector with create-new option."""

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.selectbox")
    def test_source_options_include_create_new(self, mock_selectbox, _fu, _title, mock_session):
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
        self.assertEqual(options, ["Alpha", "Beta", "+ Add new source…"])

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.selectbox", return_value="+ Add new source…")
    @patch("streamlit.markdown")
    @patch("streamlit.text_input", side_effect=["New Source", "A description"])
    @patch("streamlit.button", return_value=False)
    def test_create_new_source_shows_inputs(self, _btn, mock_input, mock_md, _sb, _fu, _title, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()

        mock_md.assert_any_call("#### Create a new source")
        self.assertEqual(mock_input.call_count, 2)


class TestUploadMdfFileUploader(unittest.TestCase):
    """C-3: File uploader accepts .txt/.mdf and shows preview."""

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
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
        self.assertEqual(kwargs[1]["type"], ["txt", "mdf"])


class TestUploadMdfParseSummary(unittest.TestCase):
    """C-5: Parse upload and display summary table."""

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_parse_and_display(self, mock_uploader, mock_expander, mock_success,
                                mock_dataframe, _sb, _title, mock_parse, mock_session):
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

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.error")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_parse_error_displayed(self, mock_uploader, mock_expander, mock_error,
                                    _sb, _title, mock_parse, mock_session):
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

    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "admin"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    def test_sample_file_parse(self, mock_uploader, mock_expander, mock_success,
                                mock_dataframe, _sb, _title, mock_session):
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
        self.assertIn("100", mock_success.call_args[0][0])
        rows = mock_dataframe.call_args[0][0]
        self.assertEqual(len(rows), 100)


class TestStageAndMatch(unittest.TestCase):
    """C-6: Stage & Match button calls stage_entries then suggest_matches."""

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.suggest_matches")
    @patch("src.services.upload_service.UploadService.stage_entries")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.dataframe")
    @patch("streamlit.success")
    @patch("streamlit.expander")
    @patch("streamlit.file_uploader")
    @patch("streamlit.button")
    @patch("streamlit.warning")
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_stage_and_match_called(self, _info, _subheader, _divider, _warning,
                                     mock_button, mock_uploader, mock_expander,
                                     mock_success, _df, _sb, _title,
                                     mock_list_batches, mock_parse, mock_stage, mock_suggest,
                                     mock_session):
        mock_sess = MagicMock()
        src = MagicMock()
        src.name = "TestSource"
        src.id = 1
        mock_sess.query.return_value.order_by.return_value.all.return_value = [src]
        mock_session.return_value = mock_sess

        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"\\lx word\n\\ps n\n\\ge thing"
        mock_file.name = "test.txt"
        mock_uploader.return_value = mock_file

        mock_expander_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_parse.return_value = [{"lx": "word", "ps": "n", "ge": "thing"}]
        mock_stage.return_value = "batch-uuid-1234"
        mock_suggest.return_value = [{"queue_id": 1, "lx": "word", "suggested_record_id": 42, "match_type": "exact"}]
        mock_list_batches.return_value = []
        mock_button.return_value = True  # Stage & Match clicked

        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()

        mock_stage.assert_called_once_with(
            user_email="test@example.com",
            source_id=1,
            entries=[{"lx": "word", "ps": "n", "ge": "thing"}],
            filename="test.txt",
        )
        mock_suggest.assert_called_once_with("batch-uuid-1234")

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.parse_upload")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="+ Add new source…")
    @patch("streamlit.file_uploader")
    @patch("streamlit.warning")
    @patch("streamlit.markdown")
    @patch("streamlit.text_input", side_effect=["", ""])
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_stage_blocked_without_source(self, _info, _subheader, _divider, _btn,
                                           _ti, _md, mock_warning, mock_uploader,
                                           _sb, _title, mock_list_batches, mock_parse,
                                           mock_session):
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
    """C-6a: Pending upload batch selector."""

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.markdown")
    def test_batch_selector_displayed(self, _md, _btn, mock_columns, _subheader, _divider,
                                       _fu, mock_selectbox, _title, mock_list_batches,
                                       mock_session):
        from datetime import datetime, timezone
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
                "uploaded_at": datetime(2026, 2, 8, 14, 52, tzinfo=timezone.utc),
            }
        ]

        col_mock = MagicMock()
        col_mock.__enter__ = MagicMock(return_value=col_mock)
        col_mock.__exit__ = MagicMock(return_value=False)
        mock_columns.return_value = [col_mock, col_mock]

        # First call is source selector, second is batch selector
        mock_selectbox.side_effect = ["TestSource", "Natick — natick.txt (50 entries, 2026-02-08 14:52)"]

        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()

        # Verify batch selector was called with correct label
        batch_call = mock_selectbox.call_args_list[1]
        self.assertIn("pending batch", batch_call[0][0].lower())
        options = batch_call[0][1]
        self.assertEqual(len(options), 1)
        self.assertIn("Natick", options[0])
        self.assertIn("50 entries", options[0])
        self.assertIn("2026-02-08 14:52", options[0])

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.list_pending_batches")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com"})
    @patch("streamlit.title")
    @patch("streamlit.selectbox", return_value="TestSource")
    @patch("streamlit.file_uploader", return_value=None)
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_no_batches_shows_info(self, mock_info, _subheader, _divider, _fu, _sb, _title,
                                    mock_list_batches, mock_session):
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess
        mock_list_batches.return_value = []

        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()

        mock_info.assert_any_call("No pending upload batches.")


class TestReMatchButton(unittest.TestCase):
    """C-6b: Re-Match button calls rematch_batch (now in dedicated review view)."""

    @patch("src.database.get_session")
    @patch("src.services.upload_service.UploadService.rematch_batch")
    @patch("streamlit.session_state", {"user_role": "editor", "user_email": "test@example.com",
                                        "review_batch_id": "abc-123"})
    @patch("streamlit.title")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.success")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    @patch("streamlit.markdown")
    @patch("streamlit.selectbox", return_value="create_new")
    @patch("streamlit.code")
    @patch("streamlit.container")
    def test_rematch_calls_service(self, mock_container, _code, _selectbox, _md,
                                    mock_info, _subheader, mock_success, mock_button,
                                    mock_columns, _title,
                                    mock_rematch, mock_session):
        mock_sess = MagicMock()
        # Empty batch so _render_review_table shows info and returns early
        mock_sess.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value = mock_sess

        mock_rematch.return_value = [
            {"queue_id": 1, "lx": "word", "suggested_record_id": 10, "match_type": "exact"}
        ]

        col_mock = MagicMock()
        col_mock.__enter__ = MagicMock(return_value=col_mock)
        col_mock.__exit__ = MagicMock(return_value=False)
        mock_columns.return_value = [col_mock, col_mock]

        # First button call is "Re-Match" (True), second is "Back to Upload" (False)
        mock_button.side_effect = [True, False]

        from src.frontend.pages.upload_mdf import upload_mdf
        upload_mdf()

        mock_rematch.assert_called_once_with("abc-123")


if __name__ == "__main__":
    unittest.main()
