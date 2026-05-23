import os
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity

def generate_artifacts(data_path, output_dir):
    print("Iniciando generación de artefactos...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Carga y limpieza de datos
    print("Cargando dataset...")
    column_names = ['user_id', 'game_title', 'behavior', 'hours', 'value']
    df = pd.read_csv(data_path, names=column_names)
    df = df.drop(columns=['value'])
    
    # 2. Filtrado para evitar ruido
    print("Filtrando datos ruidosos...")
    user_counts = df['user_id'].value_counts()
    game_counts = df['game_title'].value_counts()
    
    valid_users = user_counts[user_counts > 2].index
    valid_games = game_counts[game_counts > 5].index
    
    df_filtered = df[(df['user_id'].isin(valid_users)) & (df['game_title'].isin(valid_games))].copy()
    
    # 3. Cálculo del score implícito
    print("Calculando score implícito...")
    def calculate_score(row):
        if row['behavior'] == 'purchase':
            return 0.1
        else:
            return 1.0 + np.log1p(row['hours'])
            
    df_filtered['score'] = df_filtered.apply(calculate_score, axis=1)
    df_grouped = df_filtered.groupby(['user_id', 'game_title'])['score'].max().reset_index()
    
    # 4. Historial de usuarios
    print("Generando historial de usuarios...")
    user_history = df_grouped.groupby('user_id')['game_title'].apply(list).to_dict()
    user_history_clean = {int(k): v for k, v in user_history.items()}
    with open(os.path.join(output_dir, 'user_history.json'), 'w', encoding='utf-8') as f:
        json.dump(user_history_clean, f, ensure_ascii=False)
        
    # 5. Matriz de Similitud (Filtrado Colaborativo)
    print("Calculando matriz de similitudes (Cosine Similarity)...")
    pivot = df_grouped.pivot(index='user_id', columns='game_title', values='score').fillna(0)
    item_matrix = pivot.T
    
    similarity_matrix = cosine_similarity(item_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=item_matrix.index, columns=item_matrix.index)
    similarity_df.to_pickle(os.path.join(output_dir, 'similarity_matrix.pkl'))
    
    # 6. Cold Start Ranking Completo
    print("Generando ranking de Cold Start...")
    cold_start_ranking = df['game_title'].value_counts().index.tolist()
    with open(os.path.join(output_dir, 'cold_start_ranking.json'), 'w', encoding='utf-8') as f:
        json.dump(cold_start_ranking, f, ensure_ascii=False, indent=4)
        
    print(f"¡Artefactos generados exitosamente en {output_dir}!")

if __name__ == '__main__':
    # Para poder ejecutarlo directamente desde la consola como script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_data_path = os.path.join(base_dir, 'dataset-videojuegos.csv')
    default_output_dir = os.path.join(base_dir, 'app', 'model_artifacts')
    generate_artifacts(default_data_path, default_output_dir)
