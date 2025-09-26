from fastapi import APIRouter, Depends
from app.db import SessionLocal
from app.models import Client

router = APIRouter()

@router.get("/clients/")
def list_clients():
    db = SessionLocal()
    return db.query(Client).all()
