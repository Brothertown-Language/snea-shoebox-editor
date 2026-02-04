# Copyright (c) 2026 Brothertown Language
import unittest
import os
from src.database import _is_production, _auto_start_pgserver

class TestProductionSafety(unittest.TestCase):
    def test_production_detection(self):
        """Test that _is_production correctly identifies Streamlit Cloud environment."""
        # Mock production environment
        os.environ["STREAMLIT_RUNTIME_RELIABLE_ADDRESS"] = "some-address"
        self.assertTrue(_is_production())
        
        os.environ.pop("STREAMLIT_RUNTIME_RELIABLE_ADDRESS", None)
        os.environ["STREAMLIT_SHARING_ENVIRONMENT"] = "true"
        self.assertTrue(_is_production())
        
        # Mock local environment
        os.environ.pop("STREAMLIT_SHARING_ENVIRONMENT", None)
        self.assertFalse(_is_production())

    def test_pgserver_safety(self):
        """Test that _auto_start_pgserver never attempts to start in production."""
        # Mock production environment
        os.environ["STREAMLIT_RUNTIME_RELIABLE_ADDRESS"] = "prod"
        
        # Even if pgserver is installable (which it might be in this test env),
        # it should return None immediately because of the production check.
        result = _auto_start_pgserver()
        self.assertIsNone(result)
        
        os.environ.pop("STREAMLIT_RUNTIME_RELIABLE_ADDRESS", None)

if __name__ == "__main__":
    unittest.main()
