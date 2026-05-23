import os
import sys

# Agregamos la raíz del proyecto al path para evitar el error "ModuleNotFoundError: No module named 'app'"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))

from typing import Optional
from fastapi import FastAPI, Query
import uvicorn
from app.recommender import RecommenderEngine

app = FastAPI(title="Game Recommendation API", description="API para recomendar videojuegos usando filtrado colaborativo.")

# Inicializamos el motor de recomendaciones en el startup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model_artifacts")

print("Cargando artefactos del modelo en memoria...")
recommender = RecommenderEngine(model_dir=MODEL_DIR)
print("¡Motor de recomendación listo!")

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/recommendations")
def get_recommendations(user_id: Optional[int] = None, k: int = Query(5, ge=1, le=50)):
    """
    Retorna las top k recomendaciones de juegos para el usuario especificado.
    Si no se especifica usuario, devuelve el ranking general (Cold Start).
    """
    if user_id is None:
        recs = recommender.cold_start[:k]
    else:
        recs = recommender.get_recommendations(user_id, k=k)
    return {
        "user_id": user_id,
        "k": k,
        "recommendations": recs
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
