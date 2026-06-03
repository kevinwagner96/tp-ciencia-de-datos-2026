import os
from pydantic import BaseModel
from app.services.recommender.recommender import RecommenderEngine
from app.services.recommender.initialize_artifacts import generate_artifacts

class PurchaseRequest(BaseModel):
    game_title: str

class PlayRequest(BaseModel):
    game_title: str
    hours: float

# Inicializamos el motor de recomendaciones
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model_artifacts")

# Verificar si existe el artefacto de la matriz, si no, generarlo
sim_path = os.path.join(MODEL_DIR, "similarity_matrix.pkl")

if not os.path.exists(sim_path):
    print("Matriz de similitud no encontrada. Generándola automáticamente usando initialize_artifacts...")
    generate_artifacts(output_dir=MODEL_DIR)

print("Cargando artefactos del modelo en memoria...")
recommender = RecommenderEngine(model_dir=MODEL_DIR)
print("¡Motor de recomendación listo!")
