import os
from typing import Optional, List
from app.config import recommender
from app.services.recommender.initialize_artifacts import generate_artifacts

class RecommenderController:
    @staticmethod
    def get_recommendations(user_id: Optional[int], k: int) -> List[str]:
        return recommender.get_recommendations(user_id, k=k)

    @staticmethod
    def get_global_ranking(k: int = 50) -> List[str]:
        return recommender.get_recommendations(user_id=None, k=k)

    @staticmethod
    def retrain_model():
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(base_dir, 'model_artifacts')
        generate_artifacts(output_dir=model_dir)
        recommender.reload_matrix()
