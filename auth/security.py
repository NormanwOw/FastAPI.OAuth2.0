from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthToken:

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt
