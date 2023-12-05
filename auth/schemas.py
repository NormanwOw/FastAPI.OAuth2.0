from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, ConfigDict


class NewUser(BaseModel):
    email: EmailStr
    password: str


class UserInDB(NewUser):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID4
    disabled: bool = False
    registered: datetime


class UserData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID4
    email: EmailStr
    registered: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None
