from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserSignUp(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    re_password: str = Field(..., min_length=8)

    @validator("re_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserRead(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True

    class Config:
        from_attributes = True
