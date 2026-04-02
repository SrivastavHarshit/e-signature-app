from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document
from email_service import send_signing_email
from datetime import datetime
import os

router = APIRouter(prefix="/api/document")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fmt_size(b: int) -> str:
    if b < 1024:       return f"{b} B"
    if b < 1048576:    return f"{b/1024:.1f} KB"
    return f"{b/1048576:.1f} MB"


def fmt_date() -> str:
    # ✅ FIX: %-d is Linux-only and crashes on Windows. Use %d and strip leading zero manually.
    now = datetime.now()
    day = str(now.day)           # e.g. "3" not "03"
    month = now.strftime("%b")   # e.g. "Jul"
    year = now.strftime("%Y")    # e.g. "2025"
    return f"{day} {month} {year}"


# ── UPLOAD ────────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buf:
        buf.write(content)

    doc = Document(
        name    = file.filename,
        status  = "draft",
        size    = fmt_size(len(content)),
        created = fmt_date(),   # ✅ Windows-safe
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": "File uploaded",
        "doc": {
            "id":      doc.id,
            "name":    doc.name,
            "status":  doc.status,
            "size":    doc.size,
            "created": doc.created,
        }
    }


# ── SEND (with real emails) ───────────────────────────────────────────────
class Signer(BaseModel):
    name:  str
    email: str

class SendRequest(BaseModel):
    message:     str
    signers:     List[Signer]
    sender_name: Optional[str] = "Kayas User"

@router.post("/send/{doc_id}")
def send_document(doc_id: int, data: SendRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}

    doc.status = "sent"
    db.commit()

    sent_count = 0
    failed = []
    for signer in data.signers:
        ok = send_signing_email(
            to_name     = signer.name,
            to_email    = signer.email,
            doc_name    = doc.name,
            message     = data.message,
            sender_name = data.sender_name,
        )
        if ok:
            sent_count += 1
        else:
            failed.append(signer.email)

    response = {
        "message":     f"Document sent to {len(data.signers)} signer(s)",
        "emails_sent": sent_count,
    }
    if failed:
        response["warning"] = (
            f"Email delivery failed for: {', '.join(failed)}. "
            "Check your .env SMTP settings."
        )
    return response


# ── EDIT ─────────────────────────────────────────────────────────────────
class EditRequest(BaseModel):
    name:   Optional[str] = None
    status: Optional[str] = None

@router.put("/edit/{doc_id}")
def edit_document(doc_id: int, data: EditRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}
    if data.name:   doc.name   = data.name
    if data.status: doc.status = data.status
    db.commit()
    return {"message": "Updated", "doc": {"id": doc.id, "name": doc.name, "status": doc.status}}


# ── DELETE ────────────────────────────────────────────────────────────────
@router.delete("/delete/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        db.delete(doc)
        db.commit()
    return {"message": "Deleted"}


# ── GET ALL ───────────────────────────────────────────────────────────────
@router.get("/all")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return [
        {
            "id":      d.id,
            "name":    d.name,
            "status":  d.status,
            "size":    d.size    or "",
            "created": d.created or "",
        }
        for d in docs
    ]