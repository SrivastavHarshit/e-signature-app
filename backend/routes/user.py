from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

router = APIRouter(prefix="/api/user")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserRequest(BaseModel):
    first_name: Optional[str] = None   # added
    last_name:  Optional[str] = None   # added
    email:    str
    password: str


@router.post("/signup")
def signup(data: UserRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        return {"error": "Email already registered"}

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created"}


@router.post("/login")
def login(data: UserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email,
        User.password == data.password
    ).first()

    if user:
        return {"user_id": user.id, "name": f"{user.first_name or ''} {user.last_name or ''}".strip()}

    return {"error": "Invalid credentials"}