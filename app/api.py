import sqlite3
from fastapi import APIRouter, Query, HTTPException
from app.controllers.db.controller import DBController
from app.controllers.recommender.controller import RecommenderController
from app.config import PurchaseRequest, PlayRequest

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/admin/retrain-model")
def retrain_model():
    """
    Reentrena la matriz de similitud de filtrado colaborativo usando los datos
    actuales en la base de datos SQLite.
    """
    try:
        RecommenderController.retrain_model()
        return {"message": "Modelo reentrenado y recargado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/recomendations")
def get_user_recommendations(user_id: int, limit: int = Query(5, ge=1, le=50)):
    """
    Retorna las recomendaciones de juegos para el usuario especificado.
    Si el usuario no existe o no tiene interacciones, devuelve el ranking general (Cold Start).
    """
    recs = RecommenderController.get_recommendations(user_id, limit)
    return {
        "user_id": user_id,
        "limit": limit,
        "recommendations": recs
    }

@router.get("/games/ranking")
def get_games_ranking(limit: int = Query(50, ge=1, le=100)):
    """
    Retorna el ranking global de juegos más populares.
    """
    ranking = RecommenderController.get_global_ranking(limit)
    return {
        "limit": limit,
        "ranking": ranking
    }

@router.get("/users/{user_id}/games")
def get_user_games(user_id: int):
    """
    Retorna la lista de juegos que posee o ha jugado un usuario.
    """
    games = DBController.get_user_games(user_id)
    if not games:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no posee juegos")
    return {
        "user_id": user_id,
        "games": games
    }

@router.post("/users/{user_id}/purchase")
def record_purchase(user_id: int, request: PurchaseRequest):
    game_id = DBController.get_game_id(request.game_title)
    if not game_id:
        raise HTTPException(status_code=404, detail="Juego inexistente")
    
    if DBController.user_owns_game(user_id, game_id):
        raise HTTPException(status_code=400, detail="El usuario ya posee este juego")
    
    try:
        DBController.record_purchase(user_id, game_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": "Compra registrada exitosamente"}

@router.post("/users/{user_id}/play")
def record_play(user_id: int, request: PlayRequest):
    if request.hours <= 0:
        raise HTTPException(status_code=400, detail="Las horas deben ser mayores a 0")
        
    game_id = DBController.get_game_id(request.game_title)
    if not game_id:
        raise HTTPException(status_code=404, detail="Juego inexistente")
    
    if not DBController.user_owns_game(user_id, game_id):
        raise HTTPException(status_code=403, detail="Debe comprar el juego antes de poder jugarlo")
    
    try:
        DBController.record_play(user_id, game_id, request.hours)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": "Horas de juego registradas exitosamente"}
