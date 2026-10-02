# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-8 (behavioral) RED test: floor-clearing in-corpus calibration anchors
rank at rank 1 with cosine >= the published floor when queried through the
seam's DEFAULT threshold path (``threshold=None`` engages the calibrated
floor), with no recall regression versus the measured baseline.

Anchors and expected outcomes come exclusively from the measured calibration
evidence artifact (``src/services/calibration/gloss_space_calibration.yaml``,
provenance: production replica 2026-10-02 probe,
``tmp/1400/artifacts/verification-probe.yaml``, 6,681 embedded glosses, pin
``thenlper/gte-small``). No synthetic queries (Global Absolute Prohibition,
.opencode/guidelines/090-data-integrity.md).

The floor-clearing anchors are the in-corpus anchors whose measured cosine
clears the published floor (CALIBRATED_FLOOR = 0.93): water (1.0000), beaver
(0.9753), money (0.9970), gun (0.9959), book (0.9936). The below-floor anchor
"how many" (0.8917) is NOT part of this battery (it is SC-8a's contract).

This test FAILS (RED) because the default-floor engagement does not exist
yet: ``search_semantic(threshold=None)`` currently returns the full ranked
list without applying CALIBRATED_FLOOR, so the default path's result set is
NOT identical to the explicit-floor path and sub-floor rows leak into the
default-path results. Phase 2 implements the default engagement
(``threshold=None`` -> calibrated floor). Co-authored with AI: OpenCode
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

# Measured baseline provenance (calibration artifact -> verification probe).
FLOOR_CLEARING_ANCHORS = ("water", "beaver", "money", "gun", "book")


def _load_floor_clearing_evidence():
    """Read the measured per-anchor evidence from the calibration artifact."""
    with ARTIFACT_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    anchors = {
        str(a["query"]).strip().lower(): a
        for a in data["batteries"]["in_corpus"]["anchors"]
    }
    floor = float(data["calibrated_floor"])
    return anchors, floor


class TestFloorClearingAnchorsRecallSc8(unittest.TestCase):
    """Phase 1 Item 2 (SC-8, behavioral): recall regression battery under the
    seam's default threshold path."""

    @classmethod
    def setUpClass(cls):
        cls.anchors, cls.published_floor = _load_floor_clearing_evidence()
        cls.floor = float(CALIBRATED_FLOOR)
        # The published artifact floor and the seam's published constant must
        # agree — the battery runs against the single published floor.
        assert cls.floor == cls.published_floor, (
            f"seam CALIBRATED_FLOOR {cls.floor} != artifact calibrated_floor "
            f"{cls.published_floor}"
        )

    def test_01_every_floor_clearing_anchor_served_at_rank1_above_floor(self):
        """Each floor-clearing anchor queried via the default path (threshold
        unspecified → default floor) is served at rank 1 with cosine >= the
        published floor, hitting its measured top record."""
        for query in FLOOR_CLEARING_ANCHORS:
            with self.subTest(anchor=query):
                measured = self.anchors[query]
                result = search_semantic(mode="gloss", query=query)
                self.assertEqual(result.status, "ok", f"{query}: status {result.status}")
                self.assertTrue(result.results, f"{query}: no results under default path")
                top_id, top_score = result.results[0]
                self.assertEqual(
                    top_id,
                    int(measured["measured_top"]["record_id"]),
                    f"{query}: rank-1 record differs from measured baseline",
                )
                self.assertGreaterEqual(
                    top_score,
                    self.floor,
                    f"{query}: rank-1 cosine {top_score:.4f} below published floor {self.floor}",
                )

    def test_02_default_threshold_path_engages_the_published_floor(self):
        """The default threshold path (threshold=None) must produce the same
        result set as an explicit threshold at the published floor — i.e. the
        calibrated floor is actually engaged when the caller does not pass
        one. RED: today threshold=None returns the unfiltered ranked list."""
        for query in FLOOR_CLEARING_ANCHORS:
            with self.subTest(anchor=query):
                default_path = search_semantic(mode="gloss", query=query)
                explicit_floor = search_semantic(
                    mode="gloss", query=query, threshold=self.floor
                )
                self.assertEqual(
                    default_path.results,
                    explicit_floor.results,
                    f"{query}: default path (threshold=None) did not engage the "
                    f"published floor {self.floor}",
                )

    def test_03_default_path_serves_no_sub_floor_rows(self):
        """Under the default threshold path, no returned row sits below the
        published floor (floor-clearing anchors are served without noise)."""
        for query in FLOOR_CLEARING_ANCHORS:
            with self.subTest(anchor=query):
                result = search_semantic(mode="gloss", query=query)
                sub_floor = [rid for rid, score in result.results if score < self.floor]
                self.assertEqual(
                    sub_floor,
                    [],
                    f"{query}: {len(sub_floor)} sub-floor rows served by the "
                    f"default path (floor {self.floor} not engaged)",
                )


if __name__ == "__main__":
    unittest.main()
