from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode=True
        schema_extra={
            'example':{
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "a234d9d31673eed7ec063e3d2510493e269ee88c3aa39c0fdcedf090f3d9c331"


class LoginModel(BaseModel):
    username: str
    password: str
