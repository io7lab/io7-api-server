from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "io7@io7lab.com",
                "password": "strong!!!"
            }
        }

    class Settings:
        name = "users"

class NewUser(User):
    username: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "io7@io7lab.com",
                "password": "strong!!!",
                "username": "io7 admin"
            }
        }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
