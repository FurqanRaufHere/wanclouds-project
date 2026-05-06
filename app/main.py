# from fastapi import FastAPI
# from app.db.database import engine, Base
# from app.api.routes import router as api_router
# from app.api.auth import router as auth_router

# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="FastAPI Auth App",
#     description="""
#     FastAPI backend with JWT authentication and RBAC.
    
#     **How to use:**
#     1. POST /auth/signup — create an account
#     2. POST /auth/login  — get your JWT token
#     3. Click 'Authorize' button above, paste your token
#     4. Now you can access protected endpoints
#     """,
#     version="2.0.0"
# )

# # Register auth routes → /auth/signup, /auth/login
# app.include_router(auth_router)

# # Register API routes → /hello, /status, /predict, /admin
# app.include_router(api_router)


# @app.get("/")
# def root():
#     return {
#         "message": "API is live. Visit /docs for Swagger UI.",
#         "hint": "POST /auth/signup to create an account, POST /auth/login to get a token."
#     }


#  main.py — FastAPI application entry point
#  Removed Base.metadata.create_all()
#  WHY? Before, we let SQLAlchemy auto-create tables on startup.
#  Now Alembic owns that responsibility. Alembic creates and
#  manages tables through migration files. If we kept
#  create_all(), it would conflict with Alembic's tracking.
#
#  HOW TABLES GET CREATED NOW:
#  You run: docker exec -it fastapi_app alembic upgrade head
#  Alembic runs the migration files in alembic/versions/
#  and creates/updates tables in MySQL.
# ============================================================

from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="FastAPI Auth App",
    description="""
    FastAPI backend with JWT authentication and RBAC.

    **How to use:**
    1. POST /auth/signup — create an account
    2. POST /auth/login  — get your JWT token
    3. Click 'Authorize' button above, paste your token
    4. Now you can access protected endpoints
    """,
    version="2.0.0"
)

app.include_router(auth_router)
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "API is live. Visit /docs for Swagger UI.",
        "hint": "POST /auth/signup to create an account, POST /auth/login to get a token."
    }