# backend/app/schemas.py
# -*- coding: utf-8 -*-
"""Pydantic-схемы для API — простые DTO."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool

    class Config:
        orm_mode = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
class GroupCreate(BaseModel):
    name: str
    description: str | None = None

class GroupOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {
        "from_attributes": True  # вместо orm_mode в Pydantic v2
    }

class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None