import os
import pandas as pd
import json

class RecommenderEngine:
    def __init__(self, model_dir='model_artifacts'):
        self.model_dir = model_dir
        
        # Cargar matriz de similitud
        sim_path = os.path.join(model_dir, 'similarity_matrix.pkl')
        if os.path.exists(sim_path):
            self.similarity_df = pd.read_pickle(sim_path)
        else:
            self.similarity_df = pd.DataFrame()
            
        # Cargar historial de usuarios
        history_path = os.path.join(model_dir, 'user_history.json')
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                raw_history = json.load(f)
                self.user_history = {int(k): v for k, v in raw_history.items()}
        else:
            self.user_history = {}
            
        # Cargar ranking de cold start completo
        cold_start_path = os.path.join(model_dir, 'cold_start_ranking.json')
        if os.path.exists(cold_start_path):
            with open(cold_start_path, 'r', encoding='utf-8') as f:
                self.cold_start = json.load(f)
        else:
            self.cold_start = []

    def get_recommendations(self, user_id, k=5):
        try:
            user_id = int(user_id)
        except ValueError:
            pass

        # Cold start
        if user_id not in self.user_history:
            return self.cold_start[:k]
            
        played_games = set(self.user_history[user_id])
        
        # Nos aseguramos que los juegos jugados existan en la matriz
        valid_games = [g for g in played_games if g in self.similarity_df.columns]
        
        if not valid_games:
            return self.cold_start[:k]
            
        # Obtenemos las filas de la matriz de similitud correspondientes a los juegos que el usuario jugó
        # Sumamos las similitudes por columna (juego)
        sim_scores = self.similarity_df.loc[valid_games].sum(axis=0)
        
        # Filtramos los juegos que ya jugó
        sim_scores = sim_scores.drop(labels=valid_games, errors='ignore')
        
        # Ordenamos y nos quedamos con el top K
        top_recs = sim_scores.sort_values(ascending=False).head(k).index.tolist()
        
        return top_recs
