import pytest

from src.utils.orchestration import reset_circuit_breakers


@pytest.fixture(autouse=True)
def _reset_circuit_breakers_every_test():
    reset_circuit_breakers()
