from typing import Dict, List
from src.state import JudicialOpinion

class RubricScorer:
    """
    Handles rubric loading and multifactorial scoring (T036).
    """
    def __init__(self, rubric: Dict):
        self.rubric = rubric

    def calculate_score(self, opinions: List[JudicialOpinion]) -> int:
        if not opinions:
            return 0
        return int(sum(op.score for op in opinions) / len(opinions))
