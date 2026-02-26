from abc import ABC, abstractmethod
from typing import List, Optional
from src.state import JudicialOpinion, Evidence

class BaseReasoningStrategy(ABC):
    """
    Abstract base for judicial reasoning strategies (T034).
    (013-ironclad-hardening)
    """
    @abstractmethod
    async def evaluate(self, criterion_id: str, description: str, evidences: List[Evidence]) -> JudicialOpinion:
        pass
