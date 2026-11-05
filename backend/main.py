from database import get_connection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PokeIndex API")

# Allow our React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {"message": "Welcome to PokeIndex API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/health/database")
def database_health():
    with get_connection() as connection:
        result = connection.execute(
            "SELECT current_database()"
        ).fetchone()

    return {
        "status": "connected",
        "database": result[0],
    }