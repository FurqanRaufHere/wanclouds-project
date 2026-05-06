# from fastapi import APIRouter
# from pydantic import BaseModel

# router = APIRouter()


# # GET /hello
# @router.get("/hello")
# def say_hello():
#     return {
#         "message": "Hello from FastAPI!",
#         "status": "ok"
#     }


# # GET /status 
# @router.get("/status")
# def get_status():
#     return {
#         "service": "FastAPI Docker App",
#         "version": "1.0.0",
#         "status": "running"
#     }


# # POST /predict
# class PredictRequest(BaseModel):
#     text: str
#     threshold: float = 0.5


# class PredictResponse(BaseModel):
#     input: str
#     label: str
#     confidence: float


# @router.post("/predict", response_model=PredictResponse)
# def predict(payload: PredictRequest):
#     # mock logic — replace with a real model later
#     label = "positive" if len(payload.text) % 2 == 0 else "negative"
#     confidence = round(0.6 + (len(payload.text) % 10) * 0.03, 2)

#     return PredictResponse(
#         input=payload.text,
#         label=label,
#         confidence=confidence
#     )


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, Role
 
router = APIRouter()
 
@router.get("/hello")
def say_hello(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.username}! You are authenticated.",
        "status": "ok",
        "your_role": current_user.role
    }
 
 
@router.get("/status")
def get_status(current_user: User = Depends(get_current_user)):
    return {
        "service": "FastAPI Docker App",
        "version": "1.0.0",
        "status": "running",
        "requested_by": current_user.username
    }
 
 
class PredictRequest(BaseModel):
    text: str
    threshold: float = 0.5
 
 
class PredictResponse(BaseModel):
    input: str
    label: str
    confidence: float
    predicted_by: str   # we now know WHO made the request
 
 
@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, current_user: User = Depends(get_current_user)):
    # mock logic — replace with a real model later
    label = "positive" if len(payload.text) % 2 == 0 else "negative"
    confidence = round(0.6 + (len(payload.text) % 10) * 0.03, 2)
 
    return PredictResponse(
        input=payload.text,
        label=label,
        confidence=confidence,
        predicted_by=current_user.username  # track who called it
    )
 
@router.get("/admin")
def admin_panel(current_user: User = Depends(require_role(Role.admin))):
    return {
        "message": f"Welcome to the admin panel, {current_user.username}!",
        "note": "Only admins can see this.",
        "admin_id": current_user.id
    }