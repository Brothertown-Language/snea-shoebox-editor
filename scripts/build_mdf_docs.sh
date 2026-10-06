#!/usr/bin/env bash
# Build the MDF reference deliverables from the Toolbox source:
# pipeline: converter (JSON + LaTeX + HTML renderers) -> xelatex x2 -> PDF rename.
# Outputs: docs/mdf/build/mdf-lexical-fields-1.9a.pdf and docs/mdf/build/site/index.html
# Cover date: parsed from docs/mdf/SOURCE-PROVENANCE.md (the original document's
# date, 2006-05-12) — a missing or invalid line is a build error, never a silent
# fallback to the git date.
# Spec: issue #1379 — R-5/R-7 (SC-4, SC-6); provenance: docs/mdf/SOURCE-PROVENANCE.md.
set -euo pipefail
cd "$(dirname "$0")/.."

BUILD_DIR="docs/mdf/build"
SOURCE="docs/mdf/MDFields19a_UTF8.txt"
DELIVERABLE="$BUILD_DIR/mdf-lexical-fields-1.9a.pdf"
PROVENANCE="docs/mdf/SOURCE-PROVENANCE.md"

COVER_DATE="$(grep -m1 '^cover-date:' "$PROVENANCE" 2>/dev/null | cut -d: -f2- | tr -d ' ' || true)"
case "$COVER_DATE" in
  [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
  *)
    echo "error: no valid 'cover-date: YYYY-MM-DD' line in $PROVENANCE" >&2
    echo "       the cover date must come from the provenance file (never the git date)" >&2
    exit 1
    ;;
esac

echo "== converter: JSON + LaTeX + HTML renderers (cover date $COVER_DATE, original document)"
uv run python scripts/convert_mdf_master.py \
  --cover-date "$COVER_DATE" \
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
