# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright>=1.58.0",
# ]
#
# ///
import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def render_html_screenshot(html_path: str, output_path: str, viewport: str = "1280x800") -> str:
    width, height = [int(x) for x in viewport.split("x")]
    html_file = Path(html_path)
    out_file = Path(output_path)
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.goto(html_file.as_uri())
        await page.screenshot(path=str(out_file), full_page=True)
        await browser.close()
    return str(out_file)


def main():
    parser = argparse.ArgumentParser(description="Render HTML to screenshot PNG")
    parser.add_argument("html_path", help="Path to input HTML file")
    parser.add_argument("output_path", help="Path to output PNG file")
    parser.add_argument("--viewport", default="1280x800", help="Viewport size WxH (default: 1280x800)")
    args = parser.parse_args()
    result = asyncio.run(render_html_screenshot(args.html_path, args.output_path, args.viewport))
    print(f"Screenshot {args.html_path} -> {result}")


if __name__ == "__main__":
    main()
