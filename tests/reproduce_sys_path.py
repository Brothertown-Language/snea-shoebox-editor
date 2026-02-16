import sys
import os

def check_src_import():
    """
    Test if 'src' can be imported. 
    This simulates the environment in a Streamlit page file.
    """
    try:
        from src.logging_config import get_logger
        print("SUCCESS: 'src' is importable.")
        return True
    except ModuleNotFoundError:
        print("FAILURE: 'src' is NOT importable.")
        return False

def apply_sys_path_fix():
    """
    Simulate the fix we want to apply to page files.
    """
    # In src/frontend/pages/login.py, __file__ is /.../src/frontend/pages/login.py
    # So we need to go up 3 levels to reach the project root.
    
    # For this test file in tests/reproduce_sys_path.py, we go up 1 level.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Applied sys.path fix. Project root: {project_root}")

if __name__ == "__main__":
    print("--- Initial Check ---")
    if not check_src_import():
        print("--- Applying Fix ---")
        apply_sys_path_fix()
        print("--- Post-Fix Check ---")
        check_src_import()
