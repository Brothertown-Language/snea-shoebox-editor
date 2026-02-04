# Copyright (c) 2026 Brothertown Language
import unittest
import os
from src.database import _is_production, _auto_start_pgserver

class TestProductionSafety(unittest.TestCase):
    def test_production_detection(self):
        """Test that _is_production correctly identifies Streamlit Cloud environment."""
        # Clean up environment before each sub-test
        def clear_env():
            for key in ["STREAMLIT_RUNTIME", "STREAMLIT_CLOUD", "STREAMLIT_RUNTIME_RELIABLE_ADDRESS", "STREAMLIT_SHARING_ENVIRONMENT"]:
                os.environ.pop(key, None)

        clear_env()

        # Test STREAMLIT_RUNTIME
        os.environ["STREAMLIT_RUNTIME"] = "cloud"
        self.assertTrue(_is_production())
        clear_env()

        # Test STREAMLIT_CLOUD
        os.environ["STREAMLIT_CLOUD"] = "true"
        self.assertTrue(_is_production())
        clear_env()

        # Test STREAMLIT_RUNTIME_RELIABLE_ADDRESS
        os.environ["STREAMLIT_RUNTIME_RELIABLE_ADDRESS"] = "some-address"
        self.assertTrue(_is_production())
        clear_env()

        # Test STREAMLIT_SHARING_ENVIRONMENT
        os.environ["STREAMLIT_SHARING_ENVIRONMENT"] = "true"
        self.assertTrue(_is_production())
        clear_env()
        
        # Mock local environment
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
