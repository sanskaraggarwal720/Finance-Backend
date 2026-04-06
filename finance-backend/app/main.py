from fastapi import FastAPI
from app.routers import users, records, analytics
from app.core.database import init_db

app = FastAPI(
    title="Finance Dashboard API",
    description="Backend for a finance dashboard system with role-based access control.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(records.router, prefix="/records", tags=["Financial Records"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running."}
