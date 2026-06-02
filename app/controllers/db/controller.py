import sqlite3
import math
from app.services.db.database import get_db_connection

class DBController:
    @staticmethod
    def get_game_id(title: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM games WHERE title = ?", (title,))
        game = cursor.fetchone()
        conn.close()
        return game["id"] if game else None

    @staticmethod
    def user_owns_game(user_id: int, game_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM interactions WHERE user_id = ? AND game_id = ?", (user_id, game_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def get_user_games(user_id: int) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.title, i.behavior, i.hours 
            FROM interactions i
            JOIN games g ON i.game_id = g.id
            WHERE i.user_id = ?
        """, (user_id,))
        games = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return games

    @staticmethod
    def get_user_played_games(user_id: int) -> list[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT g.title 
            FROM interactions i
            JOIN games g ON i.game_id = g.id
            WHERE i.user_id = ?
        """, (user_id,))
        games = [row["title"] for row in cursor.fetchall()]
        conn.close()
        return games

    @staticmethod
    def get_user_game_scores(user_id: int) -> dict[str, float]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.title, i.behavior, i.hours
            FROM interactions i
            JOIN games g ON i.game_id = g.id
            WHERE i.user_id = ?
        """, (user_id,))
        scores = {}
        for row in cursor.fetchall():
            if row["behavior"] == "play":
                score = 1.0 + math.log1p(row["hours"])
            else:
                score = 0.1
            scores[row["title"]] = max(scores.get(row["title"], 0.0), score)
        conn.close()
        return scores

    @staticmethod
    def get_cold_start_ranking(k: int = 5) -> list[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        # El ranking cold_start se calcula agrupando los juegos con mas interacciones únicas
        cursor.execute("""
            SELECT g.title, COUNT(DISTINCT i.user_id) as interaction_count
            FROM interactions i
            JOIN games g ON i.game_id = g.id
            GROUP BY g.id, g.title
            ORDER BY interaction_count DESC
            LIMIT ?
        """, (k,))
        ranking = [row["title"] for row in cursor.fetchall()]
        conn.close()
        return ranking

    @staticmethod
    def record_purchase(user_id: int, game_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
            cursor.execute("""
                INSERT INTO interactions (user_id, game_id, behavior, hours)
                VALUES (?, ?, 'purchase', 1.0)
                ON CONFLICT(user_id, game_id, behavior) DO NOTHING
            """, (user_id, game_id))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def record_play(user_id: int, game_id: int, hours: float):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
            cursor.execute("""
                INSERT INTO interactions (user_id, game_id, behavior, hours)
                VALUES (?, ?, 'play', ?)
                ON CONFLICT(user_id, game_id, behavior) 
                DO UPDATE SET hours = interactions.hours + ?
            """, (user_id, game_id, hours, hours))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
