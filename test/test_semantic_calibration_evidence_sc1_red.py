# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-1 (behavioral) RED test: calibration evidence artifact exists with
per-anchor floor values and source provenance.

Target artifact: ``src/services/calibration/gloss_space_calibration.yaml``
(durable, tracked calibration evidence for the gloss-space semantic seam).

The artifact MUST record:

1. Global provenance: corpus pin (``thenlper/gte-small``), probe date, and
   the embedded-gloss count of the production replica the probe ran on.
2. Two batteries — ``in_corpus`` and ``out_of_corpus`` — each a list of
   calibration anchors, where every anchor records a real query string, a
   per-anchor floor (float), and the measured rank/cosine evidence from the
   production-replica probe. No synthetic queries, no placeholder
   provenance, no invented data (Global Absolute Prohibition,
   .opencode/guidelines/090-data-integrity.md).
3. Every anchor and battery entry carries its source provenance (where the
   query came from), and no entry is marked synthetic/generated/placeholder.

Revised-spec additions (2026-10-02 recalibration, spec change-control row 3):
the artifact's published calibrated floor MUST lie strictly within the
measured interval (0.9018, 0.9753) — strictly greater than the measured
out-of-corpus battery max ("light bulb", 0.9018) and strictly less than the
smallest floor-clearing in-corpus anchor (beaver, 0.9753) — and the artifact
MUST record provenance pointing at the measured verification probe artifact
(``tmp/1400/artifacts/verification-probe.yaml``, 2026-10-02, production
replica, 6,681 embedded glosses, pin ``thenlper/gte-small``).

This test FAILS (RED) until the GREEN step derives the calibration anchors
from real corpus queries against the production replica and publishes the
artifact. Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import pathlib
import unittest

import yaml

ARTIFACT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src"
    / "services"
    / "calibration"
    / "gloss_space_calibration.yaml"
)

CORPUS_PIN = "thenlper/gte-small"
BATTERY_TYPES = {"in_corpus", "out_of_corpus"}
SYNTHETIC_MARKERS = (
    "synthetic",
    "fabricated",
    "placeholder",
    "generated formula",
    "invented",
    "tbd",
)

# Revised-spec measured constants (spec change-control 2026-10-02 recalibration;
# provenance: tmp/1400/artifacts/verification-probe.yaml, production replica).
FLOOR_INTERVAL_LOW = 0.9018  # out-of-corpus battery max ("light bulb") — exclusive
FLOOR_INTERVAL_HIGH = 0.9753  # smallest floor-clearing in-corpus anchor (beaver) — exclusive
PROBE_ARTIFACT = "tmp/1400/artifacts/verification-probe.yaml"
PROBE_DATE = "2026-10-02"
EMBEDDED_GLOSS_COUNT = 6681

# SC-1 battery anchor lists (real queries from the measured probe battery).
IN_CORPUS_ANCHORS = ("water", "beaver", "how many", "money", "gun", "book")
OUT_OF_CORPUS_ANCHORS = (
    "coffee",
    "telephone",
    "airplane",
    "electricity",
    "car",
    "radio",
    "television",
    "computer",
    "internet",
    "light bulb",
    "clock",
    "school",
    "hospital",
    "train",
    "camera",
    "battery",
    "refrigerator",
)


class TestGlossCalibrationEvidenceSc1(unittest.TestCase):
    """Phase 1 Item 1 (SC-1, behavioral): calibration evidence artifact."""

    def setUp(self):
        self.artifact = ARTIFACT_PATH
        self.data = None
        if self.artifact.is_file():
            with self.artifact.open("r", encoding="utf-8") as fh:
                self.data = yaml.safe_load(fh)

    def test_01_artifact_exists(self):
        """The calibration evidence artifact file exists (SC-1 premise)."""
        self.assertTrue(
            self.artifact.is_file(),
            f"calibration evidence artifact missing: {self.artifact}",
        )

    def test_02_loads_as_yaml_mapping(self):
        """The artifact parses as a YAML mapping."""
        self.assertIsInstance(self.data, dict)

    def test_03_global_provenance_recorded(self):
        """Corpus pin, probe date, embedded-gloss count, and probe artifact
        path recorded (revised-spec provenance chain)."""
        prov = self.data.get("provenance", {})
        self.assertEqual(prov.get("corpus_pin"), CORPUS_PIN)
        self.assertTrue(str(prov.get("probe_date", "")).strip())
        self.assertEqual(
            str(prov.get("probe_date", ""))[:10], PROBE_DATE, "probe date is not the measured 2026-10-02 probe"
        )
        embedded = prov.get("embedded_gloss_count")
        self.assertIsInstance(embedded, int)
        self.assertEqual(embedded, EMBEDDED_GLOSS_COUNT, "embedded-gloss count must match the measured production replica")
        recorded_probe = str(prov.get("probe_artifact", "")).strip()
        self.assertTrue(recorded_probe, "provenance missing probe_artifact path")
        self.assertIn(PROBE_ARTIFACT, recorded_probe)

    def test_04_both_batteries_present_with_anchors(self):
        """Both in-corpus and out-of-corpus batteries present, non-empty."""
        batteries = self.data.get("batteries", {})
        self.assertIsInstance(batteries, dict)
        for battery_type in BATTERY_TYPES:
            self.assertIn(battery_type, batteries, battery_type)
            anchors = batteries[battery_type].get("anchors", [])
            self.assertIsInstance(anchors, list)
            self.assertGreater(len(anchors), 0, f"{battery_type}: no anchors")

    def test_05_per_anchor_floor_values_recorded(self):
        """Every anchor records a real-valued per-anchor floor."""
        for battery_type in BATTERY_TYPES:
            for anchor in self.data["batteries"][battery_type]["anchors"]:
                self.assertIn("query", anchor, anchor)
                self.assertTrue(str(anchor.get("query", "")).strip())
                floor = anchor.get("floor")
                self.assertIsInstance(floor, (int, float), anchor)
                self.assertGreater(float(floor), 0.0)
                self.assertLess(float(floor), 1.0)

    def test_06_per_anchor_probe_evidence_recorded(self):
        """Every anchor records measured rank/cosine probe evidence."""
        for battery_type in BATTERY_TYPES:
            for anchor in self.data["batteries"][battery_type]["anchors"]:
                rank = anchor.get("rank")
                self.assertIsInstance(rank, int, anchor)
                self.assertGreaterEqual(rank, 1)
                score = anchor.get("score")
                self.assertIsInstance(score, (int, float), anchor)
                # Cosine validity: 0 < score <= 1.0. The water anchor's genuine
                # exact self-match cosine IS 1.0000 (probe artifact
                # tmp/1400/artifacts/verification-probe.yaml, 2026-10-02, top hit
                # record_id 9790 'water'), so score <= 1.0 is the correct bound —
                # the earlier assertLess(score, 1.0) contradicted the revised
                # spec's measured data.
                self.assertGreater(float(score), 0.0)
                self.assertLessEqual(float(score), 1.0)

    def test_07_source_provenance_on_every_battery(self):
        """Every battery records its query-source provenance."""
        for battery_type in BATTERY_TYPES:
            battery = self.data["batteries"][battery_type]
            source = battery.get("source_provenance")
            self.assertIsInstance(source, dict, f"{battery_type}: missing source_provenance")
            recorded_description = str(source.get("description", "")).strip()
            self.assertTrue(recorded_description, f"{battery_type}: no source description")
            for marker in SYNTHETIC_MARKERS:
                self.assertNotIn(
                    marker,
                    recorded_description.lower(),
                    f"{battery_type}: synthetic provenance marker {marker!r}",
                )

    def test_08_no_synthetic_markers_anywhere(self):
        """No synthetic/placeholder markers anywhere in the artifact."""
        serialized = self.artifact.read_text(encoding="utf-8").lower()
        for marker in SYNTHETIC_MARKERS:
            self.assertNotIn(marker, serialized, f"marker {marker!r} found in artifact")

    def test_09_battery_anchor_lists_match_spec(self):
        """Battery anchors match the SC-1 real-query battery lists."""
        batteries = self.data.get("batteries", {})
        for battery_type, expected in (
            ("in_corpus", IN_CORPUS_ANCHORS),
            ("out_of_corpus", OUT_OF_CORPUS_ANCHORS),
        ):
            queries = [
                str(anchor.get("query", "")).strip().lower()
                for anchor in batteries[battery_type].get("anchors", [])
            ]
            self.assertEqual(sorted(queries), sorted(expected), f"{battery_type}: battery anchors differ from SC-1 list")

    def test_10_published_floor_within_measured_interval(self):
        """The published calibrated floor lies strictly within (0.9018, 0.9753)."""
        floor = self.data.get("calibrated_floor")
        if floor is None:
            floor = self.data.get("floor")
        self.assertIsInstance(floor, (int, float), "artifact publishes no calibrated floor constant")
        floor = float(floor)
        self.assertGreater(floor, FLOOR_INTERVAL_LOW, "floor must be strictly greater than out-of-corpus max 0.9018")
        self.assertLess(floor, FLOOR_INTERVAL_HIGH, "floor must be strictly less than smallest floor-clearing anchor 0.9753")


if __name__ == "__main__":
    unittest.main()
