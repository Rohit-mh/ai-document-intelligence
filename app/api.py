import os
import logging
from pathlib import Path
from typing import Literal, List, Optional
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

from utils.config import Config
from app.runner import get_runner
from utils.chroma_manager import get_chroma_manager, reset_chroma_database
from . import models, database, auth

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

API_VERSION = "1.0.0"

app = FastAPI(
    title="Document Intelligence System",
    description="Multi-Agent Document Intelligence API with Auth and Session Management",
    version=API_VERSION,
)

def _cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,https://gorgeous-biscotti-e746e6.netlify.app").strip()
    if os.getenv("CORS_ALLOW_ALL", "").lower() in ("1", "true", "yes"):
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()] or ["http://localhost:3000"]

_origins = _cors_allow_origins()
_cors_credentials = "*" not in _origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response Models ──

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    role: str
    content: str
    attached_doc_id: Optional[str] = None

class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)
    doc_id: Optional[str] = None
    session_id: Optional[str] = None

class SummaryRequest(BaseModel):
    doc_id: Optional[str] = None
    summary_type: Literal["concise", "detailed"] = "concise"
    session_id: Optional[str] = None

class InsightsRequest(BaseModel):
    doc_id: Optional[str] = None
    session_id: Optional[str] = None

# ── Auth Endpoints ──

@app.post("/auth/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        logger.warning(f"Login failed: User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: Incorrect password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    logger.info(f"Login successful for user: {form_data.username}")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserOut)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# ── Chat Session Endpoints ──

@app.get("/sessions", response_model=List[dict])
def get_user_sessions(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == current_user.id).order_by(models.ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in sessions]

@app.post("/sessions", response_model=dict)
def create_session(session: SessionCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    session_id = str(uuid.uuid4())
    new_session = models.ChatSession(id=session_id, user_id=current_user.id, title=session.title)
    db.add(new_session)
    db.commit()
    return {"id": session_id, "title": new_session.title}

@app.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.timestamp.asc()).all()
    return [{
        "role": m.role,
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
        "attached_doc_id": m.attached_doc_id
    } for m in messages]

# ── Core Intelligence Endpoints ──

@app.post("/ask")
def ask_question(req: QuestionRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    runner = get_runner()
    result = runner.answer_question(req.question, req.doc_id)
    
    # Save to DB if session exists
    if req.session_id:
        # Save user message
        user_msg = models.ChatMessage(session_id=req.session_id, role="user", content=req.question, attached_doc_id=req.doc_id)
        # Save assistant message
        assistant_msg = models.ChatMessage(session_id=req.session_id, role="assistant", content=result.get("answer", ""))
        db.add(user_msg)
        db.add(assistant_msg)
        
        # Update session title if it's the first message
        session = db.query(models.ChatSession).filter(models.ChatSession.id == req.session_id).first()
        if session and (session.title == "New Chat" or not session.title):
            session.title = req.question[:30] + ("..." if len(req.question) > 30 else "")
            
        db.commit()
        
    return result

@app.post("/summary")
def generate_summary(req: SummaryRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    runner = get_runner()
    if req.summary_type == "detailed":
        result = runner.get_detailed_summary(req.doc_id)
    else:
        result = runner.get_concise_summary(req.doc_id)
        
    if req.session_id:
        user_msg = models.ChatMessage(session_id=req.session_id, role="user", content=f"Generate {req.summary_type} summary", attached_doc_id=req.doc_id)
        assistant_msg = models.ChatMessage(session_id=req.session_id, role="assistant", content=result.get("summary", ""))
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
        
    return result

@app.post("/insights")
def get_insights(req: InsightsRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    runner = get_runner()
    result = runner.get_insights(req.doc_id)
    
    if req.session_id:
        user_msg = models.ChatMessage(session_id=req.session_id, role="user", content="Extract insights", attached_doc_id=req.doc_id)
        # Convert insights dict to string if needed
        content = str(result.get("raw_insights", result))
        assistant_msg = models.ChatMessage(session_id=req.session_id, role="assistant", content=content)
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
        
    return result

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    if not file.filename:
        raise HTTPException(400, "Filename is required.")
    safe_name = Path(file.filename).name
    try:
        content = await file.read()
        runner = get_runner()
        result = runner.save_and_process(safe_name, content)
        return result
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, f"Processing failed: {str(e)}")

# ── System Endpoints ──

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": API_VERSION}

@app.get("/stats")
def get_stats(current_user: models.User = Depends(auth.get_current_user)):
    runner = get_runner()
    return runner.get_stats()

@app.post("/config/validate")
def validate_config():
    return {"status": "valid", "config": Config.get_summary()}
