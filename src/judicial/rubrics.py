from src.state import JudicialOpinion


class RubricScorer:
    """
    Handles rubric loading and multifactorial scoring (T036).
    """

    def __init__(self, rubric: dict):
        self.rubric = rubric

    def calculate_score(self, opinions: list[JudicialOpinion]) -> int:
        if not opinions:
            return 0
        return int(sum(op.score for op in opinions) / len(opinions))
