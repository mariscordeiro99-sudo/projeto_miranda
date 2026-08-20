from datetime import datetime
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import hashlib
import secrets
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "FASTAPI_DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fastapi_db.sqlite'}",
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Projeto Miranda FastAPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRegister(BaseModel):
    username: str
    email: str | None = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class DocumentCreate(BaseModel):
    title: str
    content: str | None = None


class DocumentRead(DocumentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


Base.metadata.create_all(bind=engine)


def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against hash."""
    try:
        salt, hash_hex = stored_hash.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    except (ValueError, AttributeError):
        return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cria o usuário inicial somente quando as credenciais forem configuradas.
def create_initial_user():
    username = os.getenv("FASTAPI_ADMIN_USERNAME")
    password = os.getenv("FASTAPI_ADMIN_PASSWORD")
    email = os.getenv("FASTAPI_ADMIN_EMAIL") or None

    if not username or not password:
        return

    db = SessionLocal()
    existing_user = db.query(UserModel).filter(UserModel.username == username).first()
    if not existing_user:
        initial_user = UserModel(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        db.add(initial_user)
        db.commit()
    db.close()


@app.on_event("startup")
def startup_event():
    create_initial_user()


@app.get("/")
def root():
    return {
        "message": "Bem-vindo ao FastAPI do Projeto Miranda",
        "docs": "Acesse http://127.0.0.1:8000/docs para documentação da API"
    }


@app.get("/api/hello")
def hello():
    return {"message": "Olá do backend FastAPI! A comunicação está funcionando."}


@app.post("/api/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar novo usuário."""
    # Check if user exists
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user_data.username) | (UserModel.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário ou email já registrado."
        )
    
    # Create new user
    new_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = secrets.token_urlsafe(32)
    return {
        "token": token,
        "user": UserResponse.from_orm(new_user)
    }


@app.post("/api/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login usuário."""
    user = db.query(UserModel).filter(UserModel.username == credentials.username).first()
    
    if not user or not verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos."
        )
    
    token = secrets.token_urlsafe(32)
    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


@app.get("/api/documents", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    return db.query(DocumentModel).order_by(DocumentModel.id.desc()).all()


@app.post("/api/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    db_document = DocumentModel(title=document.title, content=document.content)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@app.get("/api/documents/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.get(DocumentModel, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document


@app.put("/api/documents/{document_id}", response_model=DocumentRead)
def update_document(document_id: int, document: DocumentCreate, db: Session = Depends(get_db)):
    db_document = db.get(DocumentModel, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    db_document.title = document.title
    db_document.content = document.content
    db.commit()
    db.refresh(db_document)
    return db_document


@app.delete("/api/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.get(DocumentModel, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(db_document)
    db.commit()
    return None
