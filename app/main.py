from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.auth.router import router as auth_router

app = FastAPI(
    title="FastAPI Auth App",
    version="2.0.0"
)

app.include_router(auth_router)
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "API is live. Visit /docs for Swagger UI."}
