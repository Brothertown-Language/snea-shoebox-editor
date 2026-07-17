#!/usr/bin/env bash
# build.sh — SNEA Orthography-to-Phoneme Paper Builder
#
# Usage:
#   ./build.sh                   # Full build (PDF + ePub)
#   ./build.sh 1362,1363,1364   # Partial build (comma-separated issue numbers)
#
# PDF via XeLaTeX. ePub via pandoc (LaTeX → Markdown → ePub).
# All build artifacts go to paper/build/. The paper/ directory stays clean.
# CWD-independent: resolves paths from script location.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
MASTER="$SCRIPT_DIR/master.tex"

mkdir -p "$BUILD_DIR"

XELATEX="xelatex -interaction=nonstopmode -output-directory=$BUILD_DIR"

# ---- PDF ----
if [ $# -ge 1 ]; then
    echo "Partial build: including only: $1"
    WRAPPER="$BUILD_DIR/_partial.tex"
    {
        echo "% Auto-generated partial build wrapper"
        echo "\def\includeonlysections{$1}"
        echo "\input{$MASTER}"
    } > "$WRAPPER"
    $XELATEX "$WRAPPER" 2>&1 | grep -E '^(Output|!|Warning|Error)' || true
    $XELATEX "$WRAPPER" 2>&1 | grep -E '^(Output|!|Warning|Error)' || true
    cp "$BUILD_DIR/_partial.pdf" "$BUILD_DIR/master.pdf" 2>/dev/null || true
else
    echo "Full build: all sections"
    $XELATEX "$MASTER" 2>&1 | grep -E '^(Output|!|Warning|Error)' || true
    $XELATEX "$MASTER" 2>&1 | grep -E '^(Output|!|Warning|Error)' || true
fi

echo ""
echo "PDF:  $BUILD_DIR/master.pdf"

# ---- ePub (parallel output via pandoc) ----
if command -v pandoc &>/dev/null; then
    echo "ePub: $BUILD_DIR/master.epub"

    EPUB_TMP="$BUILD_DIR/_epub"
    mkdir -p "$EPUB_TMP"

    # Convert each .tex to markdown via pandoc's native LaTeX reader
    pandoc -f latex -t markdown --wrap=none \
        -o "$EPUB_TMP/01-overview.md" \
        "$SCRIPT_DIR/section-1-overview.tex" 2>/dev/null

    for f in "$SCRIPT_DIR"/part-i-source-workflows/*.tex; do
        base=$(basename "$f" .tex)
        pandoc -f latex -t markdown --wrap=none \
            -o "$EPUB_TMP/${base}.md" "$f" 2>/dev/null
    done

    for f in "$SCRIPT_DIR"/part-ii-thematic-synthesis/*.tex; do
        base=$(basename "$f" .tex)
        pandoc -f latex -t markdown --wrap=none \
            -o "$EPUB_TMP/${base}.md" "$f" 2>/dev/null
    done

    for f in "$SCRIPT_DIR"/part-iii-external-resources/*.tex; do
        base=$(basename "$f" .tex)
        pandoc -f latex -t markdown --wrap=none \
            -o "$EPUB_TMP/${base}.md" "$f" 2>/dev/null
    done

    # Concatenate in document order
    cat "$EPUB_TMP/01-overview.md" \
        "$EPUB_TMP/1362-narragansett.md" \
        "$EPUB_TMP/1363-wampanoag-trumbull.md" \
        "$EPUB_TMP/1364-mohegan-pequot-fielding.md" \
        "$EPUB_TMP/1365-wampanoag-multi.md" \
        "$EPUB_TMP/1366-wampanoag-winslow.md" \
        "$EPUB_TMP/1367-wampanoag-wood.md" \
        "$EPUB_TMP/1368-mohegan-pequot-prince-speck.md" \
        "$EPUB_TMP/1369-mahican.md" \
        "$EPUB_TMP/preaspiration.md" \
        "$EPUB_TMP/colonial-english-phonology.md" \
        "$EPUB_TMP/vowel-ambiguity.md" \
        "$EPUB_TMP/cross-source-calibration.md" \
        "$EPUB_TMP/dialect-classification.md" \
        "$EPUB_TMP/external-resources.md" \
        "$EPUB_TMP/open-questions.md" \
        "$EPUB_TMP/linguist-feedback.md" \
        "$EPUB_TMP/future-work.md" \
        > "$EPUB_TMP/combined.md"

    pandoc "$EPUB_TMP/combined.md" -o "$BUILD_DIR/master.epub" \
        --metadata title="SNEA Orthography-to-Phoneme Conversion" \
        --metadata author="Michael Conrad" \
        --metadata lang="en" \
        --split-level=2 \
        --toc 2>/dev/null || echo "ePub build failed"

    rm -rf "$EPUB_TMP"
else
    echo "ePub: pandoc not found — skipping"
fi
