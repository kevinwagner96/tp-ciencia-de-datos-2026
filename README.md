# Sistema Recomendador de Videojuegos 🎮

Este proyecto implementa un motor de recomendación de videojuegos basado en filtrado colaborativo ítem-ítem para ofrecer sugerencias personalizadas a los usuarios. Además, aborda el problema de usuarios nuevos (Cold Start) recomendando los juegos más populares.

> [!NOTE]
> La consigna original del trabajo práctico se encuentra en el archivo [`CONSIGNA.md`](./CONSIGNA.md).

## 1. Exploración y Modelo (EDA)

Todo el análisis exploratorio de datos, limpieza, justificación de decisiones arquitectónicas y la construcción paso a paso del modelo matemático se encuentra documentado de forma interactiva en el notebook principal:

👉 **[notebooks/EDA.ipynb](./notebooks/EDA.ipynb)**

Le sugerimos leer el notebook para comprender cómo se calculan los scores implícitos, por qué se eligió la Similitud Coseno y cómo funciona la validación del modelo.

---

## 2. Cómo ejecutar el proyecto

El proyecto está diseñado para funcionar con una API REST desarrollada en **FastAPI**. En el primer inicio de la aplicación, el sistema leerá el `dataset-videojuegos.csv` y generará todos los artefactos pesados automáticamente, guardándolos en memoria para asegurar tiempos de respuesta en milisegundos.

### Requisitos Previos
Si no tenés Python o Poetry instalados en tu computadora, seguí estos pasos primero:
1. **Instalar Python (3.9 o superior):** Descargalo desde la [página oficial de Python](https://www.python.org/downloads/) e instalalo. Asegurate de marcar la opción "Add Python to PATH" durante la instalación.
2. **Instalar Poetry:** Poetry es el gestor de dependencias que usamos en este proyecto. Podés instalarlo abriendo una terminal y ejecutando:
   - En Windows (PowerShell): `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
   - En macOS/Linux: `curl -sSL https://install.python-poetry.org | python3 -`

### Instalación y Ejecución
1. Cloná este repositorio y abrí una terminal en la raíz del proyecto.
2. Instalá las dependencias. Poetry creará un entorno virtual automáticamente:
```bash
poetry install
```
3. Iniciá el servidor de la API ejecutando:
```bash
poetry run python app/main.py
```
*(Nota alternativa: Si preferís no usar el comando de poetry o ya tenés la carpeta `.venv` generada, podés correr directamente `.venv/bin/python app/main.py`)*

4. Verás en la consola que el motor carga o genera los artefactos y luego inicia el servidor en el puerto `3000`.

---

## 3. Documentación de la API

La API REST cuenta con documentación autogenerada interactiva (Swagger). Una vez iniciada la aplicación, podés acceder ingresando en tu navegador a:

👉 **http://localhost:3000/docs**

### Endpoint Principal: `/recommendations`

Este endpoint devuelve una lista de los `k` juegos recomendados para un usuario específico.

**Método:** `GET`

**Parámetros URL (Query):**
- `user_id` *(Opcional, Entero)*: El ID único del usuario para quien se piden recomendaciones. Si **no se provee**, o el usuario no existe en la base de datos (nuevo usuario), el sistema devolverá el ranking general de popularidad (Cold Start).
- `k` *(Opcional, Entero)*: Cantidad de recomendaciones deseadas. El valor por defecto es `5`. (Mínimo `1`, máximo `50`).

**Ejemplo de Petición:**
```bash
curl -X 'GET' \
  'http://localhost:3000/recommendations?user_id=207009485&k=5' \
  -H 'accept: application/json'
```

**Ejemplo de Respuesta:**
```json
{
  "user_id": 207009485,
  "k": 5,
  "recommendations": [
    "Juego Recomendado 1",
    "Juego Recomendado 2",
    "Juego Recomendado 3",
    "Juego Recomendado 4",
    "Juego Recomendado 5"
  ]
}
```
