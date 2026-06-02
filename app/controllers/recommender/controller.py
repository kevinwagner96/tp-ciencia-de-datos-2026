from typing import Optional, List
from app.config import recommender

class RecommenderController:
    @staticmethod
    def get_recommendations(user_id: Optional[int], k: int) -> List[str]:
        return recommender.get_recommendations(user_id, k=k)

    @staticmethod
    def get_global_ranking(k: int = 50) -> List[str]:
        return recommender.cold_start[:k]
