"""Phase 1 tests for the MDF Toolbox-marker converter (.issues/1379, R-1/R-2/R-8, SC-13).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "convert_mdf_master.py"
SOURCE_PATH = REPO_ROOT / "docs" / "mdf" / "MDFields19a_UTF8.txt"

_SPEC = importlib.util.spec_from_file_location("convert_mdf_master", SCRIPT_PATH)
convert_mdf_master = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(convert_mdf_master)

EXPECTED_CHAPTER_KEYS = [
    "Introduction",
    "Range_Sets",
    "Order_of_Fields",
    "Character_Style_Codes",
    "Summary_of_Fields",
    "Punctuation_and_Special_Codes",
    "Sections_in_a_Lexical_Entry",
    "Printed_Field_Labels",
    "Using_Subentries_or_Lexical_Entries",
    "Unknown_Fields",
    "Alternate_Hierarchy",
    "Formatting_and_Printing",
    "Free-form_Fields",
    "References",
    "The_MDF_Documentation",
    "Old_and_Changed_Markers",
    "When_MDF_Fails_to_Meet_Your_Requirements",
]


def source_text() -> str:
    return SOURCE_PATH.read_bytes().decode("utf-8")


def reconstruct(document: dict) -> str:
    pieces = []
    header = document["document_header"]
    pieces.extend(header["preamble"])
    pieces.extend(block["text"] for block in header["blocks"])
    for topic in document["topics"]:
        pieces.append(topic["key_text"])
        pieces.extend(topic["preamble"])
        pieces.extend(block["text"] for block in topic["blocks"])
    return "\n".join(pieces) + "\n"


def count_blocks(document: dict, marker: str) -> int:
    total = sum(1 for block in document["document_header"]["blocks"] if block["marker"] == marker)
    for topic in document["topics"]:
        total += sum(1 for block in topic["blocks"] if block["marker"] == marker)
    return total


def ftx_empty_count(document: dict) -> int:
    return sum(
        1
        for topic in document["topics"]
        for block in topic["blocks"]
        if block["marker"] == "ftx" and block["text"].split("\n", 1)[0].rstrip() == "\\ftx"
    )


def run_converter(tmp_path: Path, source: str, out_name: str = "master.json"):
    src = tmp_path / "source.txt"
    src.write_text(source, encoding="utf-8", newline="\n")
    out = tmp_path / out_name
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--source", str(src), "--out", str(out)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc, out


@pytest.fixture(scope="session")
def document():
    return convert_mdf_master.parse_mdf_text(source_text(), "docs/mdf/MDFields19a_UTF8.txt")


class TestSourceCensus:
    def test_108_key_topics(self, document):
        assert len(document["topics"]) == 108

    def test_91_marker_topics_plus_17_chapter_topics(self, document):
        chapters = [topic for topic in document["topics"] if topic["is_chapter"]]
        assert len(chapters) == 17
        assert len(document["topics"]) - len(chapters) == 91

    def test_home_entry_is_aa(self, document):
        assert document["home_key"] == "aa"
        assert document["topics"][0]["key"] == "aa"
        assert not document["topics"][0]["is_chapter"]

    def test_chapter_keys_come_from_home_toc(self, document):
        assert document["chapter_keys"] == EXPECTED_CHAPTER_KEYS

    def test_hierarchy_marker_census(self, document):
        assert count_blocks(document, "shd2") == 21
        assert count_blocks(document, "shd3") == 2
        assert count_blocks(document, "shd4") == 9

    def test_bib_nwt_and_header_census(self, document):
        assert count_blocks(document, "bib") == 4
        assert count_blocks(document, "nwt") == 2
        assert count_blocks(document, "_sh") == 1
        assert document["document_header"]["title"] == "v3.0  557  MDF Lexical Fields"

    def test_297_line_initial_cf_fields(self, document):
        assert count_blocks(document, "cf") == 297

    def test_444_examples(self, document):
        ftx_total = count_blocks(document, "ftx")
        empty = ftx_empty_count(document)
        assert ftx_total == 425
        assert empty == 11
        assert ftx_total - empty == 414
        assert count_blocks(document, "fxv") == 30
        assert (ftx_total - empty) + count_blocks(document, "fxv") == 444


class TestByteForBytePreservation:
    def test_round_trip_reconstructs_source_exactly(self, document):
        assert reconstruct(document) == source_text()

    def test_non_ascii_census_in_source(self):
        text = source_text()
        assert text.count("á") == 26
        assert text.count("ñ") == 3
        assert text.count("é") == 1
        assert text.count("•") == 2
        assert sum(1 for ch in text if ord(ch) > 127) == 32

    def test_non_ascii_survives_json_serialization(self, document):
        payload = json.dumps(document, ensure_ascii=False)
        assert payload.count("á") == 26
        assert payload.count("ñ") == 3
        assert payload.count("é") == 1
        assert payload.count("•") == 2


class TestIndentedMarkerLinesAreContent:
    def test_three_indented_cf_occurrences_are_not_fields(self, document):
        lines = source_text().split("\n")
        joined = "\n".join(block["text"] for topic in document["topics"] for block in topic["blocks"])
        for lineno in (393, 406, 2661):
            raw = lines[lineno - 1]
            assert raw.lstrip().startswith("\\cf")
            field_hits = [
                block
                for topic in document["topics"]
                for block in topic["blocks"]
                if block["marker"] == "cf" and block["line"] == lineno
            ]
            assert field_hits == []
            assert ("\n" + raw) in joined


class TestHeadings:
    def test_every_topic_except_references_has_a_heading(self, document):
        missing = [topic["key"] for topic in document["topics"] if topic["heading"] is None]
        assert missing == ["References"]

    def test_multi_shd_topic_keeps_all_shd_blocks(self, document):
        punctuation = next(t for t in document["topics"] if t["key"] == "Punctuation_and_Special_Codes")
        shd_blocks = [b for b in punctuation["blocks"] if b["marker"] == "shd"]
        assert len(shd_blocks) == 2
        assert punctuation["heading"] == "Punctuation"

    def test_multi_token_key_topic(self, document):
        last = document["topics"][-1]
        assert last["key"] == "1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d"
        assert last["heading"] == "Old verb paradigm markers"


class TestCrossReferenceTargets:
    def test_all_targets_resolve_to_topic_keys(self, document):
        keys = {topic["key"] for topic in document["topics"]}
        targets = {
            target
            for topic in document["topics"]
            for block in topic["blocks"]
            if block["marker"] == "cf"
            for target in block["targets"]
        }
        assert targets <= keys
        assert len(targets) >= 17

    def test_multi_target_cf_line(self, document):
        aa = document["topics"][0]
        cf_blocks = [b for b in aa["blocks"] if b["marker"] == "cf"]
        assert cf_blocks[1]["targets"] == ["Introduction", "Range_Sets"]

    def test_backslash_prefixed_target_resolves(self, document):
        range_sets = next(t for t in document["topics"] if t["key"] == "Range_Sets")
        first_cf = next(b for b in range_sets["blocks"] if b["marker"] == "cf")
        assert first_cf["targets"] == ["ps"]

    def test_starred_target_token_resolves(self, document):
        introduction = next(t for t in document["topics"] if t["key"] == "Introduction")
        starred = [b for b in introduction["blocks"] if b["marker"] == "cf" and "de*" in b["text"]]
        assert any("de" in b["targets"] for b in starred)


class TestSc13FailFastAndWarnContinue:
    def test_empty_source_fails_fast(self, tmp_path):
        proc, out = run_converter(tmp_path, "")
        assert proc.returncode != 0
        assert "key" in proc.stderr.lower()
        assert not out.exists()

    def test_markerless_source_fails_fast(self, tmp_path):
        proc, out = run_converter(tmp_path, "\\txt orphan content with no key\n")
        assert proc.returncode != 0
        assert "key" in proc.stderr.lower()
        assert not out.exists()

    def test_malformed_marker_warns_and_continues(self, tmp_path):
        source = "\\key kk\n\\shd K topic\n\\txt body line\n\\zzz something malformed\n"
        proc, out = run_converter(tmp_path, source)
        assert proc.returncode == 0
        assert "warning" in proc.stderr
        assert "\\zzz" in proc.stderr
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert [t["key"] for t in doc["topics"]] == ["kk"]
        assert [w["kind"] for w in doc["warnings"]] == ["malformed_marker"]
        assert doc["warnings"][0]["line"] == 4
        txt_blocks = [b for b in doc["topics"][0]["blocks"] if b["marker"] == "txt"]
        assert txt_blocks[0]["text"] == "\\txt body line\n\\zzz something malformed"

    def test_indented_marker_does_not_warn(self, tmp_path):
        source = "\\key kk\n\\shd K topic\n\\txt body\n  \\cf indented content only\n"
        proc, out = run_converter(tmp_path, source)
        assert proc.returncode == 0
        assert proc.stderr == ""
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert count_blocks(doc, "cf") == 0


class TestDuplicateKeys:
    def test_second_occurrence_warns_and_flags(self, tmp_path):
        source = "\\key dd\n\\shd First\n\\key dd\n\\shd Second\n"
        proc, out = run_converter(tmp_path, source)
        assert proc.returncode == 0
        assert "warning" in proc.stderr
        doc = json.loads(out.read_text(encoding="utf-8"))
        first, second = doc["topics"]
        assert first["occurrence"] == 1
        assert first["duplicate"] is False
        assert second["occurrence"] == 2
        assert second["duplicate"] is True
        assert [w["kind"] for w in doc["warnings"]] == ["duplicate_key"]

    def test_real_source_has_no_duplicate_keys(self, document):
        assert all(not topic["duplicate"] for topic in document["topics"])
        assert all(topic["occurrence"] == 1 for topic in document["topics"])


class TestBoundaryMinimalSource:
    def test_single_marker_source_parses(self, tmp_path):
        proc, out = run_converter(tmp_path, "\\key aa\n")
        assert proc.returncode == 0
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert len(doc["topics"]) == 1
        assert doc["topics"][0]["key"] == "aa"
        assert doc["topics"][0]["blocks"] == []
        assert doc["topics"][0]["heading"] is None


class TestContinuationPreservation:
    def test_indented_and_midline_cf_stay_inside_field(self, tmp_path):
        source = (
            "\\key kk\n"
            "\\shd K topic\n"
            "\\txt first line\n"
            "  indented \\cf mention inside content\n"
            "\\nt mid-line \\cf reference and trailing text\n"
        )
        proc, out = run_converter(tmp_path, source)
        assert proc.returncode == 0
        doc = json.loads(out.read_text(encoding="utf-8"))
        blocks = doc["topics"][0]["blocks"]
        assert count_blocks(doc, "cf") == 0
        assert blocks[1]["text"] == "\\txt first line\n  indented \\cf mention inside content"
        assert blocks[2]["text"] == "\\nt mid-line \\cf reference and trailing text"


class TestCliOnRealSource:
    def test_end_to_end_writes_valid_json(self, tmp_path):
        out = tmp_path / "master.json"
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--source", str(SOURCE_PATH), "--out", str(out)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0, proc.stderr
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert len(doc["topics"]) == 108
        assert count_blocks(doc, "cf") == 297


class TestDeterministicOutput:
    def test_parse_is_stable_across_runs(self, document):
        again = convert_mdf_master.parse_mdf_text(source_text(), "docs/mdf/MDFields19a_UTF8.txt")
        assert again == document
