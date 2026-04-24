#!/bin/bash
# Content Verification: multimodal-dispatch skill
#
# Verifies that the multimodal-dispatch skill documentation contains:
# 1. Cache TTL enforcement (REQ-3)
# 2. Cloud-first model ordering (REQ-4, REQ-8)
# 3. Cache invalidation on model events
# 4. No hardcoded model names (REQ-12)
# 5. Hybrid routing with override logging (REQ-2)
# 6. FAIL never downgraded to PASS (065-verification-honesty)
# 7. Graceful degradation / unverified modalities (REQ-5)
# 8. Nested sub-agent architecture (REQ-6)
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)

set -euo pipefail

# Resolve project directory from script location
# Script is at .opencode/tests/behaviors/multimodal-dispatch-cache.sh
# Project root is 3 levels up: behaviors/ → tests/ → .opencode/ → root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

OVERALL_RESULT=0

echo "=== Content Verification: multimodal-dispatch skill ==="

# Check 1: multimodal-dispatch SKILL.md exists and has key sections
SKILL_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/SKILL.md"
if [ -f "$SKILL_FILE" ]; then
    echo "  SKILL.md exists: PASS"

    HYBRID_ROUTING=$(grep -c "hybrid routing\|caller hint\|override" "$SKILL_FILE" 2>/dev/null || echo "0")
    if [ "$HYBRID_ROUTING" -ge 2 ]; then
        echo "  SKILL.md hybrid routing (REQ-2): PASS (found $HYBRID_ROUTING references)"
    else
        echo "  SKILL.md hybrid routing (REQ-2): FAIL (found $HYBRID_ROUTING references, need >= 2)"
        OVERALL_RESULT=1
    fi

    CLOUD_FIRST_SKILL=$(grep -c "cloud-first\|cloud first\|Cloud-first\|Cloud first\|cloud.*preferred\|preferred.*cloud" "$SKILL_FILE" 2>/dev/null || echo "0")
    if [ "$CLOUD_FIRST_SKILL" -ge 1 ]; then
        echo "  SKILL.md cloud-first policy: PASS (found $CLOUD_FIRST_SKILL references)"
    else
        echo "  SKILL.md cloud-first policy: FAIL (no cloud-first references found)"
        OVERALL_RESULT=1
    fi

    NESTED_AGENT=$(grep -c "nested\|sub-agent\|recursive\|dispatch chain" "$SKILL_FILE" 2>/dev/null || echo "0")
    if [ "$NESTED_AGENT" -ge 2 ]; then
        echo "  SKILL.md nested sub-agents (REQ-6): PASS (found $NESTED_AGENT references)"
    else
        echo "  SKILL.md nested sub-agents (REQ-6): FAIL (found $NESTED_AGENT references, need >= 2)"
        OVERALL_RESULT=1
    fi

    GRACEFUL_DEG=$(grep -c "unverified\|graceful degradation\|never block" "$SKILL_FILE" 2>/dev/null || echo "0")
    if [ "$GRACEFUL_DEG" -ge 2 ]; then
        echo "  SKILL.md graceful degradation (REQ-5): PASS (found $GRACEFUL_DEG references)"
    else
        echo "  SKILL.md graceful degradation (REQ-5): FAIL (found $GRACEFUL_DEG references, need >= 2)"
        OVERALL_RESULT=1
    fi
else
    echo "  SKILL.md exists: FAIL (file not found at $SKILL_FILE)"
    OVERALL_RESULT=1
fi

# Check 2: Probe task — cache TTL and cloud-first ordering
PROBE_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/probe.md"
if [ -f "$PROBE_FILE" ]; then
    echo "  probe.md exists: PASS"

    TTL_COUNT=$(grep -ci "ttl_seconds\|cache TTL\|300 seconds\|TTL.*300\|stale\|snapshot" "$PROBE_FILE" 2>/dev/null || echo "0")
    if [ "$TTL_COUNT" -ge 3 ]; then
        echo "  probe.md cache TTL documentation (REQ-3): PASS (found $TTL_COUNT references)"
    else
        echo "  probe.md cache TTL documentation (REQ-3): FAIL (found $TTL_COUNT references, need >= 3)"
        OVERALL_RESULT=1
    fi

    CLOUD_FIRST_PROBE=$(grep -ci "cloud-first\|cloud first\|cloud.*before\|ollama-cloud.*before\|preferred.*cloud" "$PROBE_FILE" 2>/dev/null || echo "0")
    if [ "$CLOUD_FIRST_PROBE" -ge 1 ]; then
        echo "  probe.md cloud-first ordering (REQ-4/8): PASS (found $CLOUD_FIRST_PROBE references)"
    else
        echo "  probe.md cloud-first ordering (REQ-4/8): FAIL (no cloud-first references found)"
        OVERALL_RESULT=1
    fi

    INVALIDATE_COUNT=$(grep -c "invalidate_cache\|invalidate.*cache\|rm.*capability-snapshot\|cache invalidation" "$PROBE_FILE" 2>/dev/null || echo "0")
    if [ "$INVALIDATE_COUNT" -ge 2 ]; then
        echo "  probe.md cache invalidation: PASS (found $INVALIDATE_COUNT references)"
    else
        echo "  probe.md cache invalidation: FAIL (found $INVALIDATE_COUNT references, need >= 2)"
        OVERALL_RESULT=1
    fi
else
    echo "  probe.md exists: FAIL (file not found at $PROBE_FILE)"
    OVERALL_RESULT=1
fi

# Check 3: Resolve task — hybrid routing (REQ-2)
RESOLVE_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/resolve.md"
if [ -f "$RESOLVE_FILE" ]; then
    echo "  resolve.md exists: PASS"

    HYBRID_COUNT=$(grep -c "override\|hint.*content\|caller hint\|hybrid routing\|content_derived\|MODALITY_OVERRIDE" "$RESOLVE_FILE" 2>/dev/null || echo "0")
    if [ "$HYBRID_COUNT" -ge 2 ]; then
        echo "  resolve.md hybrid routing (REQ-2): PASS (found $HYBRID_COUNT references)"
    else
        echo "  resolve.md hybrid routing (REQ-2): FAIL (found $HYBRID_COUNT references, need >= 2)"
        OVERALL_RESULT=1
    fi

    CLOUD_FIRST_RESOLVE=$(grep -ci "cloud-first\|cloud first\|cloud model\|preferred.*cloud\|cloud.*preferred" "$RESOLVE_FILE" 2>/dev/null || echo "0")
    if [ "$CLOUD_FIRST_RESOLVE" -ge 1 ]; then
        echo "  resolve.md cloud-first preference (REQ-8): PASS (found $CLOUD_FIRST_RESOLVE references)"
    else
        echo "  resolve.md cloud-first preference (REQ-8): FAIL (no cloud-first references)"
        OVERALL_RESULT=1
    fi
else
    echo "  resolve.md exists: FAIL (file not found at $RESOLVE_FILE)"
    OVERALL_RESULT=1
fi

# Check 4: Dispatch task — FAIL invariant and unverified modalities
DISPATCH_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/dispatch.md"
if [ -f "$DISPATCH_FILE" ]; then
    echo "  dispatch.md exists: PASS"

    FAIL_DOWNGRADE_COUNT=$(grep -ci "FAIL.*never.*downgrad\|downgrad.*FAIL\|never downgraded" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$FAIL_DOWNGRADE_COUNT" -ge 1 ]; then
        echo "  dispatch.md FAIL invariant (065): PASS"
    else
        echo "  dispatch.md FAIL invariant (065): FAIL (FAIL downgrade prevention not documented)"
        OVERALL_RESULT=1
    fi

    UNVERIFIED_COUNT=$(grep -c "unverified\|UNVERIFIED\|never block\|graceful" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$UNVERIFIED_COUNT" -ge 2 ]; then
        echo "  dispatch.md graceful degradation (REQ-5): PASS (found $UNVERIFIED_COUNT references)"
    else
        echo "  dispatch.md graceful degradation (REQ-5): FAIL (found $UNVERIFIED_COUNT references, need >= 2)"
        OVERALL_RESULT=1
    fi

    NESTED_DISPATCH=$(grep -c "nested\|circular\|dispatch chain" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$NESTED_DISPATCH" -ge 1 ]; then
        echo "  dispatch.md nested sub-agents (REQ-6): PASS (found $NESTED_DISPATCH references)"
    else
        echo "  dispatch.md nested sub-agents (REQ-6): FAIL (no nested dispatch references)"
        OVERALL_RESULT=1
    fi
else
    echo "  dispatch.md exists: FAIL (file not found at $DISPATCH_FILE)"
    OVERALL_RESULT=1
fi

# Check 5: No hardcoded model names in any skill file (REQ-12)
SKILL_DIR="$PROJECT_DIR/.opencode/skills/multimodal-dispatch"
HARDCODED_VIOLATIONS=0
for mdfile in "$SKILL_DIR"/SKILL.md "$SKILL_DIR"/tasks/*.md; do
    if [ -f "$mdfile" ]; then
        # Check for model names used as dispatch targets (NOT in example JSON)
        # Pattern: "use <model>", "route to <model>", "dispatch to <model>"
        HC=$(grep -ciP '(use|route to|dispatch to|select|invoke|call)\s+(glm-5|qwen3|deepseek|llama|ministra|kimi)' "$mdfile" 2>/dev/null || true)
        HC=${HC:-0}
        HARDCODED_VIOLATIONS=$((HARDCODED_VIOLATIONS + HC))
    fi
done
if [ "$HARDCODED_VIOLATIONS" -eq 0 ]; then
    echo "  no hardcoded model names as dispatch targets (REQ-12): PASS"
else
    echo "  no hardcoded model names as dispatch targets (REQ-12): FAIL (found $HARDCODED_VIOLATIONS instances)"
    OVERALL_RESULT=1
fi

# Check 6: Dispatch-multi task exists and mentions multi-modality
DISPATCH_MULTI_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/dispatch-multi.md"
if [ -f "$DISPATCH_MULTI_FILE" ]; then
    echo "  dispatch-multi.md exists: PASS"

    MULTI_COUNT=$(grep -c "multi-modality\|dispatch-multi\|multiple modali\|per-modality" "$DISPATCH_MULTI_FILE" 2>/dev/null || echo "0")
    if [ "$MULTI_COUNT" -ge 2 ]; then
        echo "  dispatch-multi.md multi-modality support: PASS (found $MULTI_COUNT references)"
    else
        echo "  dispatch-multi.md multi-modality support: FAIL (found $MULTI_COUNT references, need >= 2)"
        OVERALL_RESULT=1
    fi
else
    echo "  dispatch-multi.md exists: FAIL (file not found)"
    OVERALL_RESULT=1
fi

# Check 7: Completion task exists
COMPLETION_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/completion.md"
if [ -f "$COMPLETION_FILE" ]; then
    echo "  completion.md exists: PASS"
else
    echo "  completion.md exists: FAIL (file not found)"
    OVERALL_RESULT=1
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: multimodal-dispatch content verification"
else
    echo "FAIL: multimodal-dispatch content verification"
fi

exit $OVERALL_RESULT