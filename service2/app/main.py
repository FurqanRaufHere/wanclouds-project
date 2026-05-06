import os
import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi import Header
app = FastAPI(
    title="Service 2 — Microservice",
    description="A simple microservice that communicates with Service 1",
    version="1.0.0"
)

# Read service1's URL from environment variable
# In Docker: "http://api:8000"  (api = service name in compose)
# Locally:   "http://localhost:8000"
SERVICE1_URL = os.getenv("SERVICE1_URL", "http://localhost:8000")



#  GET /ping — Health check for service2 itself

#  Simple endpoint to confirm service2 is alive.
#  Hit this first to make sure service2 started correctly.
# ============================================================
@app.get("/ping")
def ping():
    return {
        "service": "service2",
        "status": "alive",
        "port": 8001
    }


#  GET /fetch-status — Call Service 1 and return its response

#  This is where microservice communication happens.

#  FLOW:
#  WHY is this useful in real apps?
#  Imagine a "reporting service" that needs user data from
#  an "auth service". It calls the auth service internally
#  instead of going through the public internet.
#
#  NOTE: /status on service1 requires a JWT token.
#  We pass the Authorization header through from the request
#  so service2 acts as a "proxy" for the user's token.
# ============================================================
@app.get("/fetch-status")
def fetch_status(authorization: str = Header(None)):
    """
    Calls Service 1's /status endpoint internally and returns the result.
    Pass your JWT token as: Authorization header (Bearer <token>)
    """
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        # httpx.get() makes an HTTP GET request to service1
        # timeout=5.0 means give up after 5 seconds
        response = httpx.get(
            f"{SERVICE1_URL}/status",
            headers=headers,
            timeout=5.0
        )
        return {
            "fetched_from": SERVICE1_URL,
            "status_code": response.status_code,
            "data": response.json()
        }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach Service 1 at {SERVICE1_URL}. Is it running?"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Service 1 did not respond in time."
        )

@app.get("/fetch-hello")
def fetch_hello(authorization: str = Header(None)):
    """
    Calls Service 1's /hello endpoint and returns its response.
    """
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        response = httpx.get(
            f"{SERVICE1_URL}/hello",
            headers=headers,
            timeout=5.0
        )
        return {
            "fetched_from": SERVICE1_URL,
            "status_code": response.status_code,
            "data": response.json()
        }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach Service 1 at {SERVICE1_URL}."
        )