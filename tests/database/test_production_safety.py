# Copyright (c) 2026 Brothertown Language
import unittest
import os
from src.database import _is_production, _auto_start_pgserver

class TestProductionSafety(unittest.TestCase):
    def test_production_detection(self):
        """Test that _is_production correctly identifies environment based on local files."""
        # This test is tricky because it depends on the actual presence of files in the repo.
        # However, we can use unittest.mock to simulate file existence if needed.
        from unittest.mock import patch
        
        with patch('src.database.Path.exists') as mock_exists:
            # If markers exist, it's NOT production
            mock_exists.return_value = True
            self.assertFalse(_is_production())
            
            # If markers don't exist, it IS production
            mock_exists.return_value = False
            self.assertTrue(_is_production())

    def test_pgserver_safety(self):
        """Test that _auto_start_pgserver never attempts to start in production."""
        from unittest.mock import patch
        
        # Mock production environment (no local files)
        with patch('src.database.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            # Even if pgserver is installable (which it might be in this test env),
            # it should return None immediately because of the production check.
            result = _auto_start_pgserver()
            self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
