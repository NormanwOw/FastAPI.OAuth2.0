from datetime import datetime
from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import insert, select
from jose import JWTError, jwt

from config import DATABASE_URL, settings
from auth.models import User
from auth.schemas import UserInDB, TokenData, UserData
from auth.security import pwd_context


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


engine = create_async_engine(url=DATABASE_URL)
async_session = async_sessionmaker(engine)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_user(username: str):
    async with async_session() as session:
        query = select(User).where(User.email == username)
        query = await session.execute(query)
        user = query.scalar()

        if query and user is not None:
            user = user.as_dict()

            return UserInDB(**user)

        return False


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user(token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    user = UserData(
        id=current_user.id,
        email=current_user.email,
        registered=current_user.registered
    )
    return user


async def auth_reg(email: str, password: str):
    async with async_session() as session:

        pw = get_password_hash(password)
        user = {
            'id': uuid.uuid4(), 'email': email, 'password': pw, 'registered': datetime.utcnow()
        }

        stmt = insert(User).values(user)
        await session.execute(stmt)
        await session.commit()

        del user['password']

        return user
