from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name  = Column(String, nullable=True)
    email      = Column(String, unique=True)
    password   = Column(String)

class Document(Base):
    __tablename__ = "documents"

    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)
    status  = Column(String, default="draft")
    size    = Column(String, nullable=True)   # e.g. "1.2 MB"
    created = Column(String, nullable=True)   # formatted date string