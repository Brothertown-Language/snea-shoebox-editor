# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest

from src.database.connection import _auto_start_pgserver, is_production


class TestProductionSafety(unittest.TestCase):
    def test_production_detection(self):
        """Test that is_production correctly identifies environment based on the system user."""
        from unittest.mock import MagicMock, patch

        # Patch st.secrets to raise so the secrets branch is bypassed,
        # then patch getpass module so getuser is controlled.
        mock_getpass_module = MagicMock()
        with (
            patch("src.database.connection.st") as mock_st,
            patch("src.database.connection.getpass", mock_getpass_module),
        ):
            mock_st.secrets.__contains__ = MagicMock(side_effect=Exception("no secrets"))

            # If user is 'appuser', it IS production
            mock_getpass_module.getuser.return_value = "appuser"
            self.assertTrue(is_production())

            # If user is anything else, it's NOT production
            mock_getpass_module.getuser.return_value = "muksihs"
            self.assertFalse(is_production())

            # Handle exceptions
            mock_getpass_module.getuser.side_effect = Exception("User not found")
            self.assertFalse(is_production())

    def test_pgserver_safety(self):
        """Test that _auto_start_pgserver never attempts to start in production."""
        from unittest.mock import patch

        # Patch _pg_server to None so the cache-hit branch is bypassed,
        # and patch is_production to return True so the safety check fires.
        with (
            patch("src.database.connection._pg_server", None),
            patch("src.database.connection.is_production", return_value=True),
        ):
            result = _auto_start_pgserver()
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
