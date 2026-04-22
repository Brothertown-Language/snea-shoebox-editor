# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
#
# ///
import argparse
import sys
from pathlib import Path

import yaml

REQUIRED_TOP_LEVEL_KEYS = ["metadata", "layout", "components", "navigation", "accessibility"]
METADATA_KEYS = ["spec_version", "created_by", "created_at"]
LAYOUT_KEYS = ["regions"]
COMPONENT_KEYS = ["id", "type", "label"]
NAVIGATION_KEYS = ["routes"]
ACCESSIBILITY_KEYS = ["aria_labels", "keyboard_nav", "screen_reader"]
FRAMEWORK_TERMS = frozenset(
    [
        "streamlit",
        "react",
        "vue",
        "angular",
        "svelte",
        "godot",
        "flutter",
        "android",
        "ios",
        "swiftui",
        "gtk",
        "qt",
        "wxwidgets",
        "winforms",
        "wpf",
        "nextjs",
        "nuxt",
        "remix",
    ]
)


def _check_framework_terms(data, path="") -> list[str]:
    errors = []
    if isinstance(data, str):
        lower = data.lower()
        for term in FRAMEWORK_TERMS:
            if term in lower:
                errors.append(f"Framework-specific term '{term}' found at {path}")
    elif isinstance(data, dict):
        for k, v in data.items():
            errors.extend(_check_framework_terms(v, f"{path}.{k}" if path else k))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            errors.extend(_check_framework_terms(item, f"{path}[{i}]"))
    return errors


def validate_interaction_spec(spec_path: str, schema_path: str | None = None) -> dict:
    spec_file = Path(spec_path)
    if not spec_file.exists():
        return {"valid": False, "errors": [f"Spec file not found: {spec_path}"]}
    with open(spec_file) as f:
        spec = yaml.safe_load(f)
    if spec is None:
        return {"valid": False, "errors": ["Spec file is empty"]}
    errors = []
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in spec:
            errors.append(f"Missing required top-level key: {key}")
    metadata = spec.get("metadata", {})
    for key in METADATA_KEYS:
        if key not in metadata:
            errors.append(f"Missing required metadata key: {key}")
    fw_errors = _check_framework_terms(spec)
    errors.extend(fw_errors)
    layout = spec.get("layout", {})
    if "regions" not in layout and "layout" in spec:
        errors.append("Missing required layout key: regions")
    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True, "errors": []}


def main():
    parser = argparse.ArgumentParser(description="Validate interaction spec YAML against schema")
    parser.add_argument("spec_path", help="Path to interaction spec YAML file")
    parser.add_argument("--schema-path", default=None, help="Optional path to schema YAML (reserved for future use)")
    args = parser.parse_args()
    result = validate_interaction_spec(args.spec_path, args.schema_path)
    if result["valid"]:
        print(f"VALID: {args.spec_path}")
    else:
        print(f"INVALID: {args.spec_path}")
        for err in result["errors"]:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
