"""Tests for headword-block state in MDF parser output.

Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
"""
import pytest

from src.mdf.parser import parse_mdf


def make_mdf_with_nested_va():
    """Create MDF data with both headword-block \\va and nested \\va (inside \\se subentry)."""
    return """\\lx wampum
\\va wampu-
\\ps N
\\ge ball
\\se
\\va wampum
\\ge sphere
\\nt Record: 1"""


class TestPrimaryVaField:
    """RED-phase tests for SC-P1-1: primary_va field in parsed record."""

    def test_primary_va_field_exists(self):
        """SC-P1-1: Assert 'primary_va' in record — MUST FAIL because field doesn't exist yet."""
        mdf_data = make_mdf_with_nested_va()
        records = parse_mdf(mdf_data)
        assert len(records) == 1
        record = records[0]
        assert "primary_va" in record, (
            "RED: 'primary_va' key should exist in parsed record. "
            "This MUST FAIL until _process_block_into_record() adds 'primary_va' to the record dict."
        )

    def test_primary_va_contains_only_headword_values(self):
        """SC-P1-1: Assert primary_va has only headword-block \\va values — MUST FAIL."""
        mdf_data = make_mdf_with_nested_va()
        records = parse_mdf(mdf_data)
        record = records[0]
        assert "primary_va" in record
        assert record["primary_va"] == ["wampu-"], (
            "RED: 'primary_va' should contain only headword-block \\va values (before \\se). "
            "This MUST FAIL until _process_block_into_record() captures \\va before in_headword=False."
        )


class TestExistingVaBehavior:
    """RED-phase tests for SC-P1-2: existing va list unchanged."""

    def test_va_still_contains_all_values(self):
        """SC-P1-2: Assert va list still has ALL \\va values — should PASS even before change."""
        mdf_data = make_mdf_with_nested_va()
        records = parse_mdf(mdf_data)
        record = records[0]
        assert "va" in record
        assert record["va"] == ["wampu-", "wampum"], (
            "Existing 'va' list must contain ALL \\va values (headword + nested). "
            "This should PASS even before the change."
        )
