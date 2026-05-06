#  Layer 1: get_current_user
#    → Reads the JWT from the request header
#    → Decodes it and finds the user in the database
#    → If anything is wrong: 401 Unauthorized
#
#  Layer 2: require_role("admin")
#    → Calls get_current_user first
#    → Then checks if the user's role matches
#    → If wrong role: 403 Forbidden

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#  get_current_user Layer 1: Who is making this request?
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},  # standard header for 401
    )
    # Step 1: Decode the JWT token
    payload = decode_access_token(token)
    if payload is None:
        # Token is invalid, expired, or tampered with
        raise credentials_exception

    # Step 2: Get username from the token payload
    # "sub" is the standard JWT field for "subject" (the user)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Step 3: Look up the user in the database
    # We verify the user actually exists (they might've been deleted)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # Step 4: Return the full User object
    # The route handler will receive this as a parameter
    return user

def require_role(*roles: Role):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {[r.value for r in roles]}"
            )
        return current_user
    return role_checker