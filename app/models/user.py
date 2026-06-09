import uuid
from sqlalchemy import Column, String, Enum
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Role constants
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"
    ROLES = [ROLE_ADMIN, ROLE_USER]

    # Field key constants
    ID_KEY = "id"
    USERNAME_KEY = "username"
    EMAIL_KEY = "email"
    HASHED_PASSWORD_KEY = "hashed_password"
    ROLE_KEY = "role"

    # Column length constants
    USERNAME_MAX_LEN = 50
    EMAIL_MAX_LEN = 100
    PASSWORD_HASH_LEN = 255

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String(USERNAME_MAX_LEN), unique=True, index=True, nullable=False)
    email = Column(String(EMAIL_MAX_LEN), unique=True, index=True, nullable=False)
    hashed_password = Column(String(PASSWORD_HASH_LEN), nullable=False)
    role = Column(Enum(*ROLES), default=ROLE_USER, nullable=False)

    def to_json(self) -> dict:
        return {
            self.ID_KEY: self.id,
            self.USERNAME_KEY: self.username,
            self.EMAIL_KEY: self.email,
            self.HASHED_PASSWORD_KEY: self.hashed_password,
            self.ROLE_KEY: self.role,
        }
