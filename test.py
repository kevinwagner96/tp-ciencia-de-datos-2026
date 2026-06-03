import shutil
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

from fastapi import HTTPException

from app.api import get_user_recommendations, record_play, record_purchase, retrain_model
from app.config import PlayRequest, PurchaseRequest, recommender


PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "app" / "services" / "db" / "database.db"
MODEL_PATH = PROJECT_ROOT / "app" / "model_artifacts" / "similarity_matrix.pkl"

TARGET_USER_ID = 143343409
TARGET_RECOMMENDATION = "Football Manager 2013"
SOURCE_GAMES = ("Counter-Strike Global Offensive", "Arma 3")
PLAY_HOURS = 200
LIMIT = 50


def get_users_who_played_both_games() -> list[int]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        WITH target_games AS (
            SELECT id
            FROM games
            WHERE title IN (?, ?)
        )
        SELECT user_id
        FROM interactions
        WHERE behavior = 'play'
          AND game_id IN (SELECT id FROM target_games)
        GROUP BY user_id
        HAVING COUNT(DISTINCT game_id) = 2
        ORDER BY user_id
        """,
        SOURCE_GAMES,
    )
    users = [row["user_id"] for row in cursor.fetchall()]
    conn.close()
    return users


def delete_target_game_from_user(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM interactions
        WHERE user_id = ?
          AND game_id = (SELECT id FROM games WHERE title = ?)
        """,
        (user_id, TARGET_RECOMMENDATION),
    )
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_rows


def add_target_game_to_user(user_id: int) -> tuple[str, str]:
    purchase_result = "ok"
    play_result = "ok"

    try:
        record_purchase(user_id, PurchaseRequest(game_title=TARGET_RECOMMENDATION))
    except HTTPException as exc:
        if exc.detail == "El usuario ya posee este juego":
            purchase_result = "already_owned"
        else:
            raise

    record_play(
        user_id,
        PlayRequest(game_title=TARGET_RECOMMENDATION, hours=PLAY_HOURS),
    )
    return purchase_result, play_result


def assert_game_is_recommended() -> None:
    users = get_users_who_played_both_games()
    if TARGET_USER_ID not in users:
        raise AssertionError(
            f"El usuario {TARGET_USER_ID} no jugó ambos juegos semilla: {SOURCE_GAMES}"
        )

    # El usuario objetivo no debe poseer el juego esperado, porque el recomendador
    # excluye correctamente los juegos que el usuario ya tiene o jugó.
    deleted_target_rows = delete_target_game_from_user(TARGET_USER_ID)

    before = get_user_recommendations(TARGET_USER_ID, limit=LIMIT)["recommendations"]

    purchase_results = Counter()
    play_results = Counter()
    users_to_modify = [user_id for user_id in users if user_id != TARGET_USER_ID]

    for user_id in users_to_modify:
        purchase_result, play_result = add_target_game_to_user(user_id)
        purchase_results[purchase_result] += 1
        play_results[play_result] += 1

    retrain_response = retrain_model()
    after = get_user_recommendations(TARGET_USER_ID, limit=LIMIT)["recommendations"]

    position = (
        after.index(TARGET_RECOMMENDATION) + 1
        if TARGET_RECOMMENDATION in after
        else None
    )

    print(f"Usuarios que jugaron ambos juegos: {len(users)}")
    print(f"Usuario objetivo incluido en ese grupo: {TARGET_USER_ID in users}")
    print(f"Usuarios modificados: {len(users_to_modify)}")
    print(f"Filas borradas del usuario objetivo: {deleted_target_rows}")
    print(f"Compras: {dict(purchase_results)}")
    print(f"Play {PLAY_HOURS}h: {dict(play_results)}")
    print(f"Reentrenamiento: {retrain_response}")
    print(f"Antes aparecía {TARGET_RECOMMENDATION}: {TARGET_RECOMMENDATION in before}")
    print(f"Después aparece {TARGET_RECOMMENDATION}: {TARGET_RECOMMENDATION in after}")
    print(f"Posición final: {position}")
    print("Top recomendaciones finales:")
    for index, game in enumerate(after, 1):
        marker = " <==" if game == TARGET_RECOMMENDATION else ""
        print(f"{index}. {game}{marker}")

    assert TARGET_RECOMMENDATION in after, (
        f"{TARGET_RECOMMENDATION} no apareció dentro de las {LIMIT} recomendaciones"
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        db_backup = tmp_dir_path / "database.db"
        model_backup = tmp_dir_path / "similarity_matrix.pkl"

        shutil.copy2(DB_PATH, db_backup)
        shutil.copy2(MODEL_PATH, model_backup)

        try:
            assert_game_is_recommended()
        finally:
            shutil.copy2(db_backup, DB_PATH)
            shutil.copy2(model_backup, MODEL_PATH)
            recommender.reload_matrix()
            print("Base de datos y modelo restaurados al estado previo al test.")


if __name__ == "__main__":
    main()
