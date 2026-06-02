import os
import pandas as pd
from app.controllers.db.controller import DBController

class RecommenderEngine:
    def __init__(self, model_dir='model_artifacts'):
        self.model_dir = model_dir
        self.similarity_df = pd.DataFrame()
        self.reload_matrix()

    def reload_matrix(self):
        sim_path = os.path.join(self.model_dir, 'similarity_matrix.pkl')
        if os.path.exists(sim_path):
            self.similarity_df = pd.read_pickle(sim_path)
        else:
            self.similarity_df = pd.DataFrame()
        print("Matriz de similitud recargada en memoria.")

    def get_recommendations(self, user_id=None, k=5):
        if user_id is None:
            return DBController.get_cold_start_ranking(k)
            
        try:
            user_id = int(user_id)
        except ValueError:
            pass

        user_scores = DBController.get_user_game_scores(user_id)
        
        # Cold start si el usuario no tiene interacciones registradas
        if not user_scores:
            return DBController.get_cold_start_ranking(k)
            
        owned_games = set(user_scores)
        
        # Nos aseguramos que los juegos jugados existan en la matriz
        valid_games = [g for g in owned_games if g in self.similarity_df.columns]
        
        if not valid_games:
            return DBController.get_cold_start_ranking(k)
            
        # Ponderamos las similitudes por la intensidad de preferencia del usuario.
        weights = pd.Series({game: user_scores[game] for game in valid_games})
        sim_scores = self.similarity_df.loc[valid_games].mul(weights, axis=0).sum(axis=0)
        
        # Filtramos los juegos que ya posee o jugó.
        sim_scores = sim_scores.drop(labels=owned_games, errors='ignore')
        
        # Ordenamos y nos quedamos con el top K
        top_recs = sim_scores.sort_values(ascending=False).head(k).index.tolist()
        
        return top_recs
