from src.judicial.layer import BaseReasoningStrategy
from src.state import Evidence, JudicialOpinion


class AdversarialStrategy(BaseReasoningStrategy):
    """(T035) Critical/Adversarial reasoning."""

    async def evaluate(
        self, criterion_id: str, description: str, evidences: List[Evidence]
    ) -> JudicialOpinion:
        # Simplified implementation for now
        return JudicialOpinion(
            opinion_id="adv_op",
            judge="Prosecutor",
            criterion_id=criterion_id,
            score=2,
            argument="Adversarial evaluation finding security risks.",
            cited_evidence=[],
        )


class OptimisticStrategy(BaseReasoningStrategy):
    """(T035) Reward Effort/Optimistic reasoning."""

    async def evaluate(
        self, criterion_id: str, description: str, evidences: List[Evidence]
    ) -> JudicialOpinion:
        return JudicialOpinion(
            opinion_id="opt_op",
            judge="Defense",
            criterion_id=criterion_id,
            score=4,
            argument="Optimistic evaluation highlighting partial progress.",
            cited_evidence=[],
        )
