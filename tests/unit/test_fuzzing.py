import random
import string

import pytest

from src.state import JudicialOpinion


def random_string(length=10):
    return "".join(
        random.choices(string.ascii_letters + string.digits + " \n\t", k=length)
    )


def generate_garbage_dict():
    """Generates a dictionary with random adversarial data."""
    data = {}
    for _ in range(random.randint(5, 50)):
        key = random_string(5)
        val = random.choice(
            [
                random_string(100),
                random.randint(-1000, 10000),
                random.random(),
                [random_string(5) for _ in range(5)],
                None,
                {"nested": random_string(10)},
            ]
        )
        data[key] = val
    return data


@pytest.mark.parametrize("iteration", range(50))
def test_judicial_opinion_fuzzing(iteration):
    """
    (FR-011) Fuzz testing for JudicialOpinion normalization.
    Ensures the unwrap_judicial_opinion_keys validator never crashes and
    always produces a dictionary that can be validated (or at least doesn't break logic).
    """
    garbage = generate_garbage_dict()

    # Randomly inject valid-ish keys to see if they get correctly extracted
    if random.random() > 0.5:
        garbage["rating"] = random.choice(
            [1, 2, 3, 4, 5, "5", "Score is 4/5", 0.8, -10]
        )
    if random.random() > 0.5:
        garbage["rationale"] = random_string(200)
    if random.random() > 0.5:
        garbage["criteria"] = "DIM_" + random_string(3)

    try:
        normalized = JudicialOpinion.unwrap_judicial_opinion_keys(garbage)
        assert isinstance(normalized, dict)

        # Ensure score is ALWAYS an int between 1 and 5 if it was present
        if "score" in normalized:
            assert 1 <= normalized["score"] <= 5

    except Exception as e:
        pytest.fail(
            f"Fuzzer crashed validator on iteration {iteration} with data: {garbage}. Error: {e}"
        )


def test_adversarial_score_injection():
    """Specifically test malicious or broken score formats."""
    test_cases = [
        {"score": "100"},
        {"score": -5},
        {"score": "score is 5/5"},
        {"score": 0.2},  # Should map to ~2
        {"score": "NaN"},
        {"score": None},
    ]

    for case in test_cases:
        res = JudicialOpinion.unwrap_judicial_opinion_keys(case)
        if "score" in res:
            assert 1 <= res["score"] <= 5
