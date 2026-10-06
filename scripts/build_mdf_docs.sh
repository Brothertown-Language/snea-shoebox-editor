#!/usr/bin/env bash
# Build the MDF reference deliverables from the Toolbox source:
# pipeline: converter (JSON + LaTeX + HTML renderers) -> xelatex x2 -> PDF rename.
# Outputs: docs/mdf/build/mdf-lexical-fields-1.9a.pdf and docs/mdf/build/site/index.html
# Spec: .issues/1379/spec.md — R-5/R-7 (SC-4, SC-6).
set -euo pipefail
cd "$(dirname "$0")/.."

BUILD_DIR="docs/mdf/build"
SOURCE="docs/mdf/MDFields19a_UTF8.txt"
DELIVERABLE="$BUILD_DIR/mdf-lexical-fields-1.9a.pdf"

SOURCE_DATE="$(git log -1 --format=%cs -- "$SOURCE")"
echo "== converter: JSON + LaTeX + HTML renderers (source date $SOURCE_DATE)"
uv run python scripts/convert_mdf_master.py \
  --source-date "$SOURCE_DATE" \
  --latex "$BUILD_DIR/master.tex" \
  --html-dir "$BUILD_DIR/site"

echo "== xelatex pass 1"
(
  cd "$BUILD_DIR"
  if ! xelatex -interaction=nonstopmode -halt-on-error master.tex >build-xelatex-1.log 2>&1; then
    tail -40 build-xelatex-1.log >&2
    exit 1
  fi
)
echo "== xelatex pass 2 (TOC/refs)"
(
  cd "$BUILD_DIR"
  if ! xelatex -interaction=nonstopmode -halt-on-error master.tex >build-xelatex-2.log 2>&1; then
    tail -40 build-xelatex-2.log >&2
    exit 1
  fi
  mv -f master.pdf mdf-lexical-fields-1.9a.pdf
  rm -f master.aux master.log master.out master.toc build-xelatex-1.log build-xelatex-2.log
)

test -s "$DELIVERABLE" || { echo "error: $DELIVERABLE missing or empty" >&2; exit 1; }
test -s "$BUILD_DIR/site/index.html" || { echo "error: $BUILD_DIR/site/index.html missing or empty" >&2; exit 1; }
echo "== build ok: $DELIVERABLE + $BUILD_DIR/site/index.html"
