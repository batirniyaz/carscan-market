from typing import Optional

from fastapi_users import schemas, models
from pydantic import EmailStr, ConfigDict, BaseModel


class UserRead(schemas.BaseUser[int]):
    id: models.ID
    phone_number: str
    email: EmailStr = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    phone_number: str
    email: EmailStr = None
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class PhoneNumberLoginRequest(BaseModel):
    phone_number: str
    password: str
