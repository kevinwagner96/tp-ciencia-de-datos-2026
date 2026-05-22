from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Ping Pong API")

@app.get("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
