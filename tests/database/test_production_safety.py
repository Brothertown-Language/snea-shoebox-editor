# Copyright (c) 2026 Brothertown Language
import unittest
import os
from src.database import _is_production, _auto_start_pgserver

class TestProductionSafety(unittest.TestCase):
    def test_production_detection(self):
        """Test that _is_production correctly identifies environment based on the system user."""
        from unittest.mock import patch
        
        with patch('src.database.getpass.getuser') as mock_getuser:
            # If user is 'appuser', it IS production
            mock_getuser.return_value = "appuser"
            self.assertTrue(_is_production())
            
            # If user is anything else, it's NOT production
            mock_getuser.return_value = "muksihs"
            self.assertFalse(_is_production())
            
            # Handle exceptions
            mock_getuser.side_effect = Exception("User not found")
            self.assertFalse(_is_production())

    def test_pgserver_safety(self):
        """Test that _auto_start_pgserver never attempts to start in production."""
        from unittest.mock import patch
        
        # Mock production environment (user is appuser)
        with patch('src.database.getpass.getuser') as mock_getuser:
            mock_getuser.return_value = "appuser"
            
            # Even if pgserver is installable (which it might be in this test env),
            # it should return None immediately because of the production check.
            result = _auto_start_pgserver()
            self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
