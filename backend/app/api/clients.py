from fastapi import APIRouter, Depends
from app.db import SessionLocal
from app.models import Client
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import SessionLocal
from .. import models
from ..api.auth import get_current_user

router = APIRouter(prefix="/clients", tags=["clients"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ClientCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

@router.get("/", response_model=List[dict])
def list_clients(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    clients = db.query(models.Client).all()
    return [{"id": c.id, "full_name": c.full_name, "email": c.email, "phone": c.phone} for c in clients]

@router.post("/", response_model=dict)
def create_client(data: ClientCreate, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    client = models.Client(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": client.id, "full_name": client.full_name, "email": client.email, "phone": client.phone}

