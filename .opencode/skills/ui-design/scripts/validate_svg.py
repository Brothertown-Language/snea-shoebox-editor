# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "lxml>=5.0.0",
# ]
#
# ///
import argparse
import sys
from pathlib import Path

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
SVG_SCHEMA = [
    ("root_tag", f"{{{SVG_NS}}}svg"),
    ("viewBox_attr", "viewBox"),
    ("named_groups", ["header", "content", "footer", "sidebar"]),
]

REQUIRED_REGIONS = {"header", "content", "footer"}


def validate_svg(svg_path: str) -> dict:
    svg_file = Path(svg_path)
    if not svg_file.exists():
        return {"valid": False, "errors": [f"File not found: {svg_path}"]}
    try:
        tree = etree.parse(str(svg_file))
    except etree.XMLSyntaxError as e:
        return {"valid": False, "errors": [f"XML syntax error: {e}"]}
    root = tree.getroot()
    errors = []
    if root.tag != SVG_SCHEMA[0][1]:
        local = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if local != "svg":
            errors.append(f"Root element is '{local}', expected 'svg'")
    if "viewBox" not in root.attrib:
        errors.append("Missing required 'viewBox' attribute on root <svg>")
    found_regions = set()
    for g in root.iter(f"{{{SVG_NS}}}g"):
        gid = g.attrib.get("id", "")
        if gid in SVG_SCHEMA[2][1]:
            found_regions.add(gid)
    missing = REQUIRED_REGIONS - found_regions
    if missing:
        errors.append(f"Missing required named groups: {sorted(missing)}")
    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True, "errors": []}


def main():
    parser = argparse.ArgumentParser(description="Validate SVG structure for ui-design wireframes")
    parser.add_argument("svg_path", help="Path to SVG file to validate")
    args = parser.parse_args()
    result = validate_svg(args.svg_path)
    if result["valid"]:
        print(f"VALID: {args.svg_path}")
    else:
        print(f"INVALID: {args.svg_path}")
        for err in result["errors"]:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
