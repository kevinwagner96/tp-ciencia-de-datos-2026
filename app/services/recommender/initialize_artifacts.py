import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.db.database import get_db_connection

def generate_artifacts(output_dir):
    print("Iniciando generación de artefactos desde SQLite...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Carga de datos desde SQLite
    print("Cargando interacciones...")
    conn = get_db_connection()
    query = """
        SELECT i.user_id, g.title as game_title, i.behavior, i.hours 
        FROM interactions i
        JOIN games g ON i.game_id = g.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # El dataset puede tener dos filas para el mismo usuario-juego:
    # una compra y otra con las horas jugadas. Para modelar preferencias,
    # agregamos primero a una única observación por usuario-juego.
    user_game = (
        df.assign(
            purchase_score=np.where(df['behavior'] == 'purchase', 0.1, 0.0),
            play_score=np.where(df['behavior'] == 'play', 1.0 + np.log1p(df['hours']), 0.0),
        )
        .groupby(['user_id', 'game_title'], as_index=False)
        .agg(
            purchase_score=('purchase_score', 'max'),
            play_score=('play_score', 'max'),
        )
    )
    user_game['score'] = user_game[['purchase_score', 'play_score']].max(axis=1)
    
    # 2. Filtrado para evitar ruido
    print("Filtrando datos ruidosos...")
    user_counts = user_game['user_id'].value_counts()
    game_counts = user_game['game_title'].value_counts()
    
    valid_users = user_counts[user_counts > 2].index
    valid_games = game_counts[game_counts > 5].index
    
    df_filtered = user_game[
        (user_game['user_id'].isin(valid_users)) &
        (user_game['game_title'].isin(valid_games))
    ].copy()
    
    if df_filtered.empty:
        print("Advertencia: No hay suficientes datos para generar la matriz después del filtrado.")
        return
    
    # 4. Matriz de Similitud (Filtrado Colaborativo)
    print("Calculando matriz de similitudes (Cosine Similarity)...")
    pivot = df_filtered.pivot(index='user_id', columns='game_title', values='score').fillna(0)
    item_matrix = pivot.T
    
    similarity_matrix = cosine_similarity(item_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=item_matrix.index, columns=item_matrix.index)
    similarity_df.to_pickle(os.path.join(output_dir, 'similarity_matrix.pkl'))
    
    print(f"¡Matriz de similitudes generada exitosamente en {output_dir}!")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_output_dir = os.path.join(base_dir, 'model_artifacts')
    generate_artifacts(default_output_dir)
