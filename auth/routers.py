from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from config import settings
from auth.schemas import UserData, NewUser
from auth.security import AuthToken
from auth.auth import authenticate_user, get_current_active_user, auth_reg, get_user
from auth.schemas import Token


router = APIRouter(
    tags=['User']
)


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthToken.create_access_token(
        data={'sub': user.email},
        expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/users/me/')
async def read_users_me(
    current_user: Annotated[UserData, Depends(get_current_active_user)]
):
    return current_user


@router.post('/registration', status_code=201)
async def registration(user: NewUser):
    if await get_user(user.email):
        response = {'detail': 'register user already exists'}
        return JSONResponse(content=response, status_code=400)

    new_user = await auth_reg(user.email, user.password)
    return new_user
