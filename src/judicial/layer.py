from abc import ABC, abstractmethod

from src.state import Evidence, JudicialOpinion


class BaseReasoningStrategy(ABC):
    """
    Abstract base for judicial reasoning strategies (T034).
    (013-ironclad-hardening)
    """

    @abstractmethod
    async def evaluate(
        self,
        criterion_id: str,
        description: str,
        evidences: list[Evidence],
    ) -> JudicialOpinion:
        pass
