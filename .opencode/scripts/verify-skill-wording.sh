#!/bin/bash
# Verification tool for Unit 12 - Checks for remaining Junie language patterns

echo "=== Skill Wording Quality Verification ==="
echo ""

FOUND_ISSUES=0

echo "1. Checking for 'invoked automatically'..."
grep -r --include="*.md" "invoked automatically" .opencode/skills/ .opencode/guidelines/ AGENTS.md 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "2. Checking for 'Operating Protocol'..."
grep -r --include="*.md" "Operating Protocol" .opencode/skills/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "3. Checking for 'Entry Criteria'..."
grep -r --include="*.md" "Entry Criteria" .opencode/skills/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "4. Checking for 'Exit Criteria'..."
grep -r --include="*.md" "Exit Criteria" .opencode/skills/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "5. Checking for 'Auto-invoke'..."
grep -r --include="*.md" "Auto-invoke" .opencode/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "6. Checking for 'auto-invoke'..."
grep -r --include="*.md" "auto-invoke" .opencode/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "7. Checking for 'Automatic Invocation'..."
grep -r --include="*.md" "Automatic Invocation" .opencode/ AGENTS.md 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "8. Checking for hardcoded identity examples..."
grep -r --include="*.md" "OpenCode (ollama-cloud/glm-5)" .opencode/skills/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "9. Checking for 'Sneh Kothari'..."
grep -r --include="*.md" "Sneh Kothari" .opencode/skills/ 2>/dev/null
if [ $? -eq 0 ]; then
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

echo ""
echo "=== Verification Complete ==="
if [ $FOUND_ISSUES -gt 0 ]; then
    echo ""
    echo "❌ FOUND $FOUND_ISSUES issue(s) above"
    echo "   Fix the highlighted occurrences before proceeding to Unit 13"
    exit 1
else
    echo ""
    echo "✅ No Junie language patterns found"
    echo "   All skill wording is compliant"
    exit 0
fi
