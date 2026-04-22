# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cairosvg>=2.7.0",
# ]
#
# ///
import argparse
from pathlib import Path

import cairosvg


def render_svg_to_png(svg_path: str, output_path: str, dpi: int = 96) -> str:
    svg_file = Path(svg_path)
    out_file = Path(output_path)
    if not svg_file.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    scale = dpi / 96.0
    cairosvg.svg2png(
        url=str(svg_file),
        write_to=str(out_file),
        scale=scale,
    )
    return str(out_file)


def main():
    parser = argparse.ArgumentParser(description="Render SVG to PNG")
    parser.add_argument("svg_path", help="Path to input SVG file")
    parser.add_argument("output_path", help="Path to output PNG file")
    parser.add_argument("--dpi", type=int, default=96, help="Output DPI (default: 96)")
    args = parser.parse_args()
    result = render_svg_to_png(args.svg_path, args.output_path, args.dpi)
    print(f"Rendered {args.svg_path} -> {result}")


if __name__ == "__main__":
    main()
