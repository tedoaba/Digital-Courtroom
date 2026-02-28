"""
Unit tests for batch response parsing (FR-005).
Covers: Partial JSON responses, corrupt/malformed entries, and mapping back to individual retries.
"""

from pydantic import ValidationError

from src.state import JudicialOpinion as StateOpinion


class TestBatchParsingLogic:
    """Tests for US3 batch parsing requirements."""

    def test_parse_valid_batch(self):
        """Standard valid JSON list should parse correctly."""
        raw_json = [
            {
                "opinion_id": "Judge_DIM1_123",
                "judge": "Prosecutor",
                "criterion_id": "DIM1",
                "score": 4,
                "argument": "Arg 1",
                "cited_evidence": ["ev1"],
            },
            {
                "opinion_id": "Judge_DIM2_123",
                "judge": "Prosecutor",
                "criterion_id": "DIM2",
                "score": 5,
                "argument": "Arg 2",
                "cited_evidence": ["ev2"],
            },
        ]

        # Validating using Pydantic
        opinions = [StateOpinion(**item) for item in raw_json]
        assert len(opinions) == 2
        assert opinions[0].criterion_id == "DIM1"
        assert opinions[1].criterion_id == "DIM2"

    def test_partial_success_with_missing_items(self):
        """FR-005: Identify missing IDs when batch only returns subset."""
        requested_ids = ["DIM1", "DIM2", "DIM3"]
        received_json = [
            {"criterion_id": "DIM1", "score": 4},
            {"criterion_id": "DIM3", "score": 2},
        ]

        received_ids = {item["criterion_id"] for item in received_json}
        missing_ids = [rid for rid in requested_ids if rid not in received_ids]

        assert "DIM2" in missing_ids
        assert len(missing_ids) == 1

    def test_corrupt_entries_discarded(self):
        """FR-005: Corrupt/malformed entries are logged and discarded."""
        batch = [
            {
                "criterion_id": "DIM1",
                "score": 4,
                "judge": "Prosecutor",
                "opinion_id": "1",
                "argument": "A",
                "cited_evidence": [],
            },
            {
                "criterion_id": "DIM2",
                "score": "invalid",
                "judge": "Prosecutor",
            },  # Corrupt score
            {"malformed": "data"},  # Missing required fields
        ]

        valid_opinions = []
        corrupt_items = []

        for item in batch:
            try:
                valid_opinions.append(StateOpinion(**item))
            except (ValidationError, TypeError, KeyError):
                corrupt_items.append(item)

        assert len(valid_opinions) == 1
        assert len(corrupt_items) == 2
        assert valid_opinions[0].criterion_id == "DIM1"
