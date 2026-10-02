# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-8a (behavioral) RED test: the in-corpus anchor "how many" (measured
top cosine 0.8917) falls below the published calibrated floor
(CALIBRATED_FLOOR = 0.93) by measurement and MUST return the below-floor
empty outcome under the default threshold path — ``ok`` + empty ``results``
+ the pinned SC-5 message "No gloss results meet the sensitivity floor." —
NOT a rank-1 serve.

Anchors and expected outcomes come exclusively from the measured calibration
evidence artifact (``src/services/calibration/gloss_space_calibration.yaml``,
provenance: production replica 2026-10-02 probe,
``tmp/1400/artifacts/verification-probe.yaml``, 6,681 embedded glosses, pin
``thenlper/gte-small``). No synthetic queries (Global Absolute Prohibition,
.opencode/guidelines/090-data-integrity.md). This is documented measured
overlap behavior, not recall regression.

This test FAILS (RED) because the below-floor empty outcome is not yet
implemented: ``search_semantic(threshold=None)`` currently returns the full
ranked list (rank-1 serve) with the ranked-count message, never the pinned
SC-5 deficiency message. Phase 2 seam work implements the default-floor
engagement and the SC-5 below-floor outcome. Co-authored with AI: OpenCode
(zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import pathlib
import unittest

import yaml

from src.services.semantic_search_service import CALIBRATED_FLOOR, search_semantic

ARTIFACT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src"
    / "services"
    / "calibration"
    / "gloss_space_calibration.yaml"
)

# Pinned SC-5 deficiency message (spec constant, not an example).
PINNED_BELOW_FLOOR_MESSAGE = "No gloss results meet the sensitivity floor."

BELOW_FLOOR_ANCHOR = "how many"


def _load_below_floor_evidence():
    """Read the measured per-anchor evidence from the calibration artifact."""
    with ARTIFACT_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    anchors = {
        str(a["query"]).strip().lower(): a
        for a in data["batteries"]["in_corpus"]["anchors"]
    }
    floor = float(data["calibrated_floor"])
    return anchors, floor


class TestBelowFloorAnchorHowManySc8a(unittest.TestCase):
    """Phase 1 Item 3 (SC-8a, behavioral): "how many" returns the below-floor
    empty outcome under the default threshold path."""

    @classmethod
    def setUpClass(cls):
        cls.anchors, cls.published_floor = _load_below_floor_evidence()
        cls.floor = float(CALIBRATED_FLOOR)
        assert BELOW_FLOOR_ANCHOR in cls.anchors, (
            f"anchor {BELOW_FLOOR_ANCHOR!r} missing from calibration artifact"
        )
        # The published artifact floor and the seam's published constant must
        # agree — the battery runs against the single published floor.
        assert cls.floor == cls.published_floor, (
            f"seam CALIBRATED_FLOOR {cls.floor} != artifact calibrated_floor "
            f"{cls.published_floor}"
        )

    def test_01_measured_top_score_is_below_the_published_floor(self):
        """Measurement precondition (passes at calibration-artifact level):
        the anchor's measured top cosine is strictly below the published
        floor — this is what makes the SC-8a contract applicable."""
        measured = self.anchors[BELOW_FLOOR_ANCHOR]
        self.assertLess(
            float(measured["score"]),
            self.floor,
            f"{BELOW_FLOOR_ANCHOR}: measured score {measured['score']} not "
            f"below published floor {self.floor}",
        )
        self.assertEqual(
            int(measured["measured_top"]["record_id"]),
            3400,
            f"{BELOW_FLOOR_ANCHOR}: measured top record differs from baseline "
            "(record 3400 'One.')",
        )

    def test_02_below_floor_anchor_returns_empty_outcome_not_rank1_serve(self):
        """Queried via the default threshold path, "how many" (measured top
        cosine 0.8917 < published floor 0.93) MUST return status ok with an
        EMPTY results list — never a rank-1 serve. RED: today the seam serves
        the full ranked list (rank 1 = record 3400) because no default floor
        is engaged."""
        result = search_semantic(mode="gloss", query=BELOW_FLOOR_ANCHOR)
        self.assertEqual(
            result.status,
            "ok",
            f"{BELOW_FLOOR_ANCHOR}: expected below-floor ok status, got "
            f"{result.status!r}",
        )
        self.assertEqual(
            result.results,
            [],
            f"{BELOW_FLOOR_ANCHOR}: measured below-floor anchor was served "
            f"as ranked results ({len(result.results)} rows, top "
            f"{result.results[0] if result.results else None}) — rank-1 serve "
            f"instead of the below-floor empty outcome",
        )

    def test_03_below_floor_empty_outcome_carries_pinned_sc5_message(self):
        """The below-floor empty outcome carries the pinned SC-5 deficiency
        message exactly: "No gloss results meet the sensitivity floor."
        RED: today the ranked-serve path returns the count message, never
        the pinned deficiency message."""
        result = search_semantic(mode="gloss", query=BELOW_FLOOR_ANCHOR)
        self.assertEqual(
            result.message,
            PINNED_BELOW_FLOOR_MESSAGE,
            f"{BELOW_FLOOR_ANCHOR}: expected pinned SC-5 message "
            f"{PINNED_BELOW_FLOOR_MESSAGE!r}, got {result.message!r}",
        )

    def test_04_default_path_outcome_matches_explicit_floor_outcome(self):
        """Parity: the default threshold path for "how many" must produce the
        same empty outcome as an explicit threshold at the published floor.
        RED: today the default path is unfiltered while the explicit-floor
        call already returns the threshold-empty outcome."""
        default_path = search_semantic(mode="gloss", query=BELOW_FLOOR_ANCHOR)
        explicit_floor = search_semantic(
            mode="gloss", query=BELOW_FLOOR_ANCHOR, threshold=self.floor
        )
        self.assertEqual(
            default_path.results,
            explicit_floor.results,
            f"{BELOW_FLOOR_ANCHOR}: default path (threshold=None) did not "
            f"engage the published floor {self.floor}",
        )
        self.assertEqual(
            default_path.message,
            explicit_floor.message,
            f"{BELOW_FLOOR_ANCHOR}: default path message differs from "
            "explicit-floor path message",
        )


if __name__ == "__main__":
    unittest.main()
