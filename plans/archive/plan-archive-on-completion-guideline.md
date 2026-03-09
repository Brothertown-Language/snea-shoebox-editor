# Plan: Revise Guidelines — Archive Completed Plans Immediately

**Status:** ✔️ Completed

## Problem

The agent keeps leaving completed plans as pending or completed without archiving them. The current
rules say to archive "immediately before calling `submit`" — a deferred trigger that the agent
routinely skips or forgets.

## Goal

Strengthen the archiving rule in both `plan_standards.md` and `01-approval-gate.md` so that
archiving is triggered **immediately when the last step of a plan is confirmed**, not deferred
to a pre-submit scan.

## Steps

1. 🔄 `plan_standards.md` — Revise the **Archiving** section and **Pre-Submit Checklist** to state
   that archiving MUST happen immediately upon last-step confirmation, and that deferring archiving
   to pre-submit is a CRITICAL VIOLATION.

2. 🔄 `guidelines/01-approval-gate.md` — Revise the **Archiving Mandate** paragraph to match:
   immediate archiving upon last-step confirmation; deferral is a CRITICAL VIOLATION.

3. 🔄 Verify both files reflect the new rule consistently.
