import os
import sys

# Agregamos la raíz del proyecto al path para evitar el error "ModuleNotFoundError: No module named 'app'"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))

from fastapi import FastAPI
import uvicorn
from app.services.db.initialize_db import populate_db
from app.api import router as api_router

app = FastAPI(title="Game Recommendation API", description="API para recomendar videojuegos usando filtrado colaborativo.")

# Inicializar y poblar BD SQLite si es necesario
print("Verificando estado de la base de datos SQLite...")
populate_db()

# Incluir las rutas (endpoints) separadas en app/api.py
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3001, reload=True)
