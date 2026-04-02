from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import document, user
from database import engine
from models import Base
import os

# ✅ FIX: Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routes
app.include_router(user.router)
app.include_router(document.router)

# serve frontend
@app.get("/", response_class=HTMLResponse)
def home():
    with open("../frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()