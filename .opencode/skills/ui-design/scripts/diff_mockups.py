# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "Pillow>=10.0.0",
# ]
#
# ///
import argparse
from pathlib import Path

from PIL import Image, ImageChops


def diff_mockups(before_path: str, after_path: str, output_path: str) -> str:
    before_file = Path(before_path)
    after_file = Path(after_path)
    out_file = Path(output_path)
    if not before_file.exists():
        raise FileNotFoundError(f"Before image not found: {before_path}")
    if not after_file.exists():
        raise FileNotFoundError(f"After image not found: {after_path}")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    img_before = Image.open(before_file).convert("RGB")
    img_after = Image.open(after_file).convert("RGB")
    if img_before.size != img_after.size:
        img_after = img_after.resize(img_before.size)
    diff = ImageChops.difference(img_before, img_after)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    diff.save(str(out_file))
    return str(out_file)


def main():
    parser = argparse.ArgumentParser(description="Visual diff of two mockup images")
    parser.add_argument("before_path", help="Path to before image")
    parser.add_argument("after_path", help="Path to after image")
    parser.add_argument("output_path", help="Path to output diff image")
    args = parser.parse_args()
    result = diff_mockups(args.before_path, args.after_path, args.output_path)
    print(f"Diff saved: {result}")


if __name__ == "__main__":
    main()
