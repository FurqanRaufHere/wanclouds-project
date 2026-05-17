import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AUTH_LOGIN_URL = "/auth/login"


class SQLAlchemyConfig:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "appuser")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "apppassword")
    MYSQL_DB = os.getenv("MYSQL_DB", "appdb")


DATABASE_URL = (
    f"mysql+pymysql://{SQLAlchemyConfig.MYSQL_USER}:{SQLAlchemyConfig.MYSQL_PASSWORD}"
    f"@{SQLAlchemyConfig.MYSQL_HOST}:{SQLAlchemyConfig.MYSQL_PORT}/{SQLAlchemyConfig.MYSQL_DB}"
)
