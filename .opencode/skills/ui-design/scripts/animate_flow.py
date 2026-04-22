# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright>=1.58.0",
#     "pyyaml>=6.0",
# ]
#
# ///
import argparse
import asyncio
from pathlib import Path

import yaml
from playwright.async_api import async_playwright


async def animate_flow(interaction_spec_path: str, output_dir: str) -> list[str]:
    spec_file = Path(interaction_spec_path)
    out_dir = Path(output_dir)
    if not spec_file.exists():
        raise FileNotFoundError(f"Interaction spec not found: {interaction_spec_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(spec_file) as f:
        spec = yaml.safe_load(f)
    routes = spec.get("navigation", {}).get("routes", [])
    spec.get("navigation", {}).get("transitions", [])
    screenshots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        for idx, route in enumerate(routes):
            await page.set_content(f"<html><body><h1>{route.get('path', 'unknown')}</h1></body></html>")
            out_path = out_dir / f"step_{idx:03d}.png"
            await page.screenshot(path=str(out_path))
            screenshots.append(str(out_path))
        await browser.close()
    return screenshots


def main():
    parser = argparse.ArgumentParser(description="Animate interaction spec flow")
    parser.add_argument("interaction_spec_path", help="Path to interaction spec YAML")
    parser.add_argument("output_dir", help="Output directory for screenshot sequence")
    args = parser.parse_args()
    result = asyncio.run(animate_flow(args.interaction_spec_path, args.output_dir))
    for path in result:
        print(f"Captured: {path}")


if __name__ == "__main__":
    main()
