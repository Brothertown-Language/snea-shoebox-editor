import os
import ast
import pytest
from src.services.navigation_service import NavigationService

# List of all valid Page objects from NavigationService
VALID_PAGES = [
    NavigationService.PAGE_LOGIN,
    NavigationService.PAGE_STATUS,
    NavigationService.PAGE_HOME,
    NavigationService.PAGE_USER,
    NavigationService.PAGE_RECORDS,
    NavigationService.PAGE_UPLOAD,
    NavigationService.PAGE_BATCH_ROLLBACK,
    NavigationService.PAGE_TABLE_MAINTENANCE,
    NavigationService.PAGE_LOGOUT,
]

# Extract valid url_paths. StreamlitPage object doesn't expose the original file path
# easily in all versions, so we use the ones we know from NavigationService.
VALID_URL_PATHS = [
    "login",
    "status",
    "index",
    "profile",
    "records",
    "upload",
    "rollback",
    "maintenance",
    "logout",
]

# We also know the valid file paths from NavigationService.py
VALID_FILE_PATHS = [
    "src/frontend/pages/login.py",
    "src/frontend/pages/system_status.py",
    "src/frontend/pages/index.py",
    "src/frontend/pages/user_info.py",
    "src/frontend/pages/records.py",
    "src/frontend/pages/upload_mdf.py",
    "src/frontend/pages/batch_rollback.py",
    "src/frontend/pages/table_maintenance.py",
    "src/frontend/pages/logout.py",
]

def test_no_hardcoded_streamlit_navigation():
    """
    Ensure no files use hardcoded strings for st.switch_page() that don't match
    the centralized Page objects in NavigationService.
    
    This helps prevent the StreamlitAPIException: Could not find page: `...`
    """
    project_root = os.getcwd()
    src_dir = os.path.join(project_root, "src")
    
    violations = []
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                violations.extend(check_file_for_hardcoded_navigation(file_path))
    
    if violations:
        message = "Detected hardcoded st.switch_page calls with invalid or non-centralized paths:\n"
        for v in violations:
            message += f"- {v['file']}:{v['line']}: {v['call']}\n"
        pytest.fail(message)

def check_file_for_hardcoded_navigation(file_path):
    violations = []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return []
            
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and 
            isinstance(node.func, ast.Attribute) and 
            node.func.attr == "switch_page" and 
            isinstance(node.func.value, ast.Name) and 
            node.func.value.id == "st"):
            
            # Check if the first argument is a constant string
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                path = node.args[0].value
                # If it's a hardcoded string, it MUST match one of our registered url_paths or paths
                # But ideally, we want to move towards using Page objects entirely.
                # For now, we at least enforce that if they use strings, they must be valid.
                if path not in VALID_FILE_PATHS and path not in VALID_URL_PATHS:
                    violations.append({
                        "file": os.path.relpath(file_path),
                        "line": node.lineno,
                        "call": f"st.switch_page(\"{path}\")"
                    })
    return violations
