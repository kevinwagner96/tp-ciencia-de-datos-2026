import os
from pydantic import BaseModel
from app.services.recommender.recommender import RecommenderEngine
from app.services.recommender.initialize_artifacts import generate_artifacts

class PurchaseRequest(BaseModel):
    user_id: int
    game_title: str

class PlayRequest(BaseModel):
    user_id: int
    game_title: str
    hours: float

# Inicializamos el motor de recomendaciones
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model_artifacts")

# Verificar si existen los artefactos, si no, generarlos
sim_path = os.path.join(MODEL_DIR, "similarity_matrix.pkl")
history_path = os.path.join(MODEL_DIR, "user_history.json")
cold_start_path = os.path.join(MODEL_DIR, "cold_start_ranking.json")

if not (os.path.exists(sim_path) and os.path.exists(history_path) and os.path.exists(cold_start_path)):
    print("Artefactos no encontrados. Generándolos automáticamente usando initialize_artifacts...")
    DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "dataset-videojuegos.csv")
    generate_artifacts(data_path=DATA_PATH, output_dir=MODEL_DIR)

print("Cargando artefactos del modelo en memoria...")
recommender = RecommenderEngine(model_dir=MODEL_DIR)
print("¡Motor de recomendación listo!")
