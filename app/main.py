from alembic import command
from fastapi import FastAPI
from alembic.config import Config
from app.api.auth.router import router as auth_router
from app.api.cars import router as cars_router

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


run_migrations()

app = FastAPI(
    title="FastAPI Auth App",
    version="2.0.0"
)

app.include_router(auth_router)
app.include_router(cars_router)



@app.get("/")
def root():
    return {"message": "API is live. Visit /docs for Swagger UI."}
