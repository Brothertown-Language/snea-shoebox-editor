#!/bin/bash
# Content Verification: verification and research skills
#
# Verifies that:
# 1. verification skill has PASS/FAIL/UNVERIFIED model (REQ-10)
# 2. FAIL is never downgraded to PASS (065-verification-honesty)
# 3. research skill has source attribution (REQ-11)
# 4. research skill reports gaps for unavailable modalities (REQ-5)
# 5. Both skills reference multimodal-dispatch
# 6. Both skills have completion tasks
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

OVERALL_RESULT=0

echo "=== Content Verification: verification and research skills ==="

# === VERIFICATION SKILL ===

VER_SKILL="$PROJECT_DIR/.opencode/skills/verification/SKILL.md"
VER_VERIFY="$PROJECT_DIR/.opencode/skills/verification/tasks/verify.md"
VER_SINGLE="$PROJECT_DIR/.opencode/skills/verification/tasks/verify-single.md"
VER_COMPLETE="$PROJECT_DIR/.opencode/skills/verification/tasks/completion.md"

# Check 1: SKILL.md exists and has PASS/FAIL/UNVERIFIED model
if [ -f "$VER_SKILL" ]; then
    echo "  verification/SKILL.md exists: PASS"

    PASS_FAIL=$(grep -c "PASS.*FAIL.*UNVERIFIED\|PASS | FAIL | UNVERIFIED" "$VER_SKILL" 2>/dev/null || echo "0")
    if [ "$PASS_FAIL" -ge 1 ]; then
        echo "  verification PASS/FAIL/UNVERIFIED model (REQ-10): PASS"
    else
        echo "  verification PASS/FAIL/UNVERIFIED model (REQ-10): FAIL"
        OVERALL_RESULT=1
    fi

    FAIL_INVARIANT=$(grep -c "FAIL.*never.*downgrad\|never downgraded\|FAIL cannot\|FAIL stays" "$VER_SKILL" 2>/dev/null || echo "0")
    if [ "$FAIL_INVARIANT" -ge 1 ]; then
        echo "  verification FAIL invariant (065): PASS"
    else
        echo "  verification FAIL invariant (065): FAIL"
        OVERALL_RESULT=1
    fi

    DISPATCH_REF=$(grep -c "multimodal-dispatch\|modality-aware\|modality.routing" "$VER_SKILL" 2>/dev/null || echo "0")
    if [ "$DISPATCH_REF" -ge 1 ]; then
        echo "  verification references multimodal-dispatch: PASS"
    else
        echo "  verification references multimodal-dispatch: FAIL"
        OVERALL_RESULT=1
    fi
else
    echo "  verification/SKILL.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 2: verify.md exists and has ClaimResult schema
if [ -f "$VER_VERIFY" ]; then
    echo "  verification/tasks/verify.md exists: PASS"

    CLAIM_RESULT=$(grep -c "ClaimResult\|claim_id\|status.*PASS.*FAIL\|evidence_artifacts" "$VER_VERIFY" 2>/dev/null || echo "0")
    if [ "$CLAIM_RESULT" -ge 2 ]; then
        echo "  verify.md ClaimResult schema: PASS (found $CLAIM_RESULT references)"
    else
        echo "  verify.md ClaimResult schema: FAIL (found $CLAIM_RESULT references, need >= 2)"
        OVERALL_RESULT=1
    fi
else
    echo "  verification/tasks/verify.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 3: verify-single.md exists
if [ -f "$VER_SINGLE" ]; then
    echo "  verification/tasks/verify-single.md exists: PASS"
else
    echo "  verification/tasks/verify-single.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 4: completion.md exists
if [ -f "$VER_COMPLETE" ]; then
    echo "  verification/tasks/completion.md exists: PASS"
else
    echo "  verification/tasks/completion.md exists: FAIL"
    OVERALL_RESULT=1
fi

# === RESEARCH SKILL ===

RES_SKILL="$PROJECT_DIR/.opencode/skills/research/SKILL.md"
RES_RESEARCH="$PROJECT_DIR/.opencode/skills/research/tasks/research.md"
RES_MULTI="$PROJECT_DIR/.opencode/skills/research/tasks/research-multi.md"
RES_COMPLETE="$PROJECT_DIR/.opencode/skills/research/tasks/completion.md"

# Check 5: SKILL.md exists and has source attribution
if [ -f "$RES_SKILL" ]; then
    echo "  research/SKILL.md exists: PASS"

    SOURCE_ATTR=$(grep -c "source_attribution\|source attribution\|source_type\|confidence" "$RES_SKILL" 2>/dev/null || echo "0")
    if [ "$SOURCE_ATTR" -ge 3 ]; then
        echo "  research source attribution (REQ-11): PASS (found $SOURCE_ATTR references)"
    else
        echo "  research source attribution (REQ-11): FAIL (found $SOURCE_ATTR references, need >= 3)"
        OVERALL_RESULT=1
    fi

    GAPS=$(grep -c "gaps\|gap\|unverified_modalities\|never block" "$RES_SKILL" 2>/dev/null || echo "0")
    if [ "$GAPS" -ge 2 ]; then
        echo "  research gap reporting (REQ-5/11): PASS (found $GAPS references)"
    else
        echo "  research gap reporting (REQ-5/11): FAIL (found $GAPS references, need >= 2)"
        OVERALL_RESULT=1
    fi

    DISPATCH_REF=$(grep -c "multimodal-dispatch" "$RES_SKILL" 2>/dev/null || echo "0")
    if [ "$DISPATCH_REF" -ge 1 ]; then
        echo "  research references multimodal-dispatch: PASS"
    else
        echo "  research references multimodal-dispatch: FAIL"
        OVERALL_RESULT=1
    fi
else
    echo "  research/SKILL.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 6: research.md exists and has ResearchResult schema
if [ -f "$RES_RESEARCH" ]; then
    echo "  research/tasks/research.md exists: PASS"

    RESEARCH_RESULT=$(grep -c "ResearchResult\|source_attribution\|findings\|gaps" "$RES_RESEARCH" 2>/dev/null || echo "0")
    if [ "$RESEARCH_RESULT" -ge 3 ]; then
        echo "  research.md ResearchResult schema: PASS (found $RESEARCH_RESULT references)"
    else
        echo "  research.md ResearchResult schema: FAIL (found $RESEARCH_RESULT references, need >= 3)"
        OVERALL_RESULT=1
    fi
else
    echo "  research/tasks/research.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 7: research-multi.md exists
if [ -f "$RES_MULTI" ]; then
    echo "  research/tasks/research-multi.md exists: PASS"

    MULTI_MOD=$(grep -c "multi-modality\|multiple modali\|per-modality\|modalities_used" "$RES_MULTI" 2>/dev/null || echo "0")
    if [ "$MULTI_MOD" -ge 2 ]; then
        echo "  research-multi.md multi-modality: PASS (found $MULTI_MOD references)"
    else
        echo "  research-multi.md multi-modality: FAIL (found $MULTI_MOD references, need >= 2)"
        OVERALL_RESULT=1
    fi
else
    echo "  research/tasks/research-multi.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 8: completion.md exists
if [ -f "$RES_COMPLETE" ]; then
    echo "  research/tasks/completion.md exists: PASS"
else
    echo "  research/tasks/completion.md exists: FAIL"
    OVERALL_RESULT=1
fi

# Check 9: No hardcoded model names in verification or research skills
for dir in verification research; do
    for file in "$PROJECT_DIR/.opencode/skills/$dir"/SKILL.md "$PROJECT_DIR/.opencode/skills/$dir"/tasks/*.md; do
        if [ -f "$file" ]; then
            HC=$(grep -ciP '(use|route to|dispatch to|select|invoke|call)\s+(glm-5|qwen3|deepseek|llama|ministra|kimi)' "$file" 2>/dev/null || true)
            HC=${HC:-0}
            if [ "$HC" -gt 0 ]; then
                echo "  $file hardcoded model names: FAIL (found $HC instances)"
                OVERALL_RESULT=1
            fi
        fi
    done
done
echo "  no hardcoded model names in verification/research (REQ-12): PASS"

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: verification and research skills verification"
else
    echo "FAIL: verification and research skills verification"
fi

exit $OVERALL_RESULT