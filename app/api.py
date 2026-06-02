import sqlite3
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.controllers.db.controller import DBController
from app.controllers.recommender.controller import RecommenderController
from app.config import PurchaseRequest, PlayRequest

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.get("/recommendations")
def get_recommendations(user_id: Optional[int] = None, k: int = Query(5, ge=1, le=50)):
    """
    Retorna las top k recomendaciones de juegos para el usuario especificado.
    Si no se especifica usuario, devuelve el ranking general (Cold Start).
    """
    recs = RecommenderController.get_recommendations(user_id, k)
    return {
        "user_id": user_id,
        "k": k,
        "recommendations": recs
    }

@router.get("/ranking")
def get_ranking(k: int = Query(50, ge=1, le=100)):
    """
    Retorna el ranking global de juegos más populares.
    """
    ranking = RecommenderController.get_global_ranking(k)
    return {
        "k": k,
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

@router.post("/interactions/purchase")
def record_purchase(request: PurchaseRequest):
    game_id = DBController.get_game_id(request.game_title)
    if not game_id:
        raise HTTPException(status_code=404, detail="Juego inexistente")
    
    if DBController.user_owns_game(request.user_id, game_id):
        raise HTTPException(status_code=400, detail="El usuario ya posee este juego")
    
    try:
        DBController.record_purchase(request.user_id, game_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": "Compra registrada exitosamente"}

@router.post("/interactions/play")
def record_play(request: PlayRequest):
    if request.hours <= 0:
        raise HTTPException(status_code=400, detail="Las horas deben ser mayores a 0")
        
    game_id = DBController.get_game_id(request.game_title)
    if not game_id:
        raise HTTPException(status_code=404, detail="Juego inexistente")
    
    if not DBController.user_owns_game(request.user_id, game_id):
        raise HTTPException(status_code=403, detail="Debe comprar el juego antes de poder jugarlo")
    
    try:
        DBController.record_play(request.user_id, game_id, request.hours)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": "Horas de juego registradas exitosamente"}
