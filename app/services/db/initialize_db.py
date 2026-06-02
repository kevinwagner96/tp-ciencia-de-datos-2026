import os
import sys
import pandas as pd

SERVICES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(SERVICES_DIR)
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(PROJECT_ROOT)

from app.services.db.database import get_db_connection, init_db

DATA_PATH = os.path.join(PROJECT_ROOT, "dataset-videojuegos.csv")

def populate_db():
    print("Iniciando creación de la base de datos SQLite...")
    init_db()
    
    conn = get_db_connection()
    
    # Check if DB is already populated
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    if cursor.fetchone()[0] > 0:
        print("La base de datos SQLite ya contiene datos. Saltando poblamiento inicial.")
        conn.close()
        return

    print("Cargando dataset para poblar SQLite...")
    column_names = ['user_id', 'game_title', 'behavior', 'hours', 'value']
    df = pd.read_csv(DATA_PATH, names=column_names)
    
    # Insert users
    print("Insertando usuarios...")
    unique_users = df[['user_id']].drop_duplicates().rename(columns={'user_id': 'id'})
    unique_users.to_sql('users', conn, if_exists='append', index=False)
    
    # Insert games
    print("Insertando juegos...")
    unique_games = df[['game_title']].drop_duplicates().rename(columns={'game_title': 'title'})
    unique_games.to_sql('games', conn, if_exists='append', index=False)
    
    # Mapear game_title a game_id
    print("Mapeando juegos a IDs...")
    games_df = pd.read_sql_query("SELECT id as game_id, title as game_title FROM games", conn)
    df = df.merge(games_df, on='game_title')
    
    # Procesar interacciones
    print("Procesando interacciones (agrupando horas jugadas)...")
    
    # Para compras, eliminamos duplicados y fijamos horas en 1.0
    purchases = df[df['behavior'] == 'purchase'][['user_id', 'game_id', 'behavior']].copy()
    purchases['hours'] = 1.0
    purchases = purchases.drop_duplicates(subset=['user_id', 'game_id', 'behavior'])
    
    # Para horas de juego, sumamos las horas de cada usuario por juego
    plays = df[df['behavior'] == 'play'].groupby(['user_id', 'game_id', 'behavior'])['hours'].sum().reset_index()
    
    # Concatenar ambas tablas
    interactions = pd.concat([purchases, plays], ignore_index=True)
    
    print("Insertando interacciones...")
    interactions.to_sql('interactions', conn, if_exists='append', index=False)
    
    conn.close()
    print("¡Base de datos SQLite poblada exitosamente!")

if __name__ == "__main__":
    populate_db()
