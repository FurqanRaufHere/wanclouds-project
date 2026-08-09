import inspect
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db_session
from app.core.security import decode_access_token
from app.core.config import AUTH_LOGIN_URL
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_LOGIN_URL)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def authenticate(func):
    """Route decorator that gates access behind get_current_user, instead of
    declaring the dependency on every endpoint signature or at the router level."""
    sig = inspect.signature(func)
    if "current_user" in sig.parameters:
        return func

    current_user_param = inspect.Parameter(
        "current_user",
        kind=inspect.Parameter.KEYWORD_ONLY,
        default=Depends(get_current_user),
        annotation=User,
    )
    new_sig = sig.replace(parameters=[*sig.parameters.values(), current_user_param])

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            kwargs.pop("current_user", None)
            return await func(*args, **kwargs)

        async_wrapper.__signature__ = new_sig
        return async_wrapper

    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs.pop("current_user", None)
        return func(*args, **kwargs)

    wrapper.__signature__ = new_sig
    return wrapper
