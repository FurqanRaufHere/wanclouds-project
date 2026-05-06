from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

#  POST /auth/signup: Create a new user
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - username: must be unique
    - email: must be unique and valid format
    - password: will be hashed, never stored as plain text
    """
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken. Please choose another."
        )

    # Check if email is already registered
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please log in instead."
        )

    # Hash the password before saving
    # user_data.password = "mypassword123"
    # hashed           = "$2b$12$eImi..."
    hashed = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed
        # role defaults to "user" as defined in the model
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

#  POST /auth/login — Authenticate and get a token
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    # "sub" (subject) is the standard JWT field for user identity
    # We also embed "role" so we can check it without a DB lookup
    token = create_access_token(data={
        "sub": user.username,
        "role": user.role.value
    })

    return Token(access_token=token, token_type="bearer")