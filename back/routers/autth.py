#авторизация и вход
# main.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from typing import Optional

app = FastAPI()

# ── 1. БД ──────────────────────────────────────────────────────────────
engine = create_engine("sqlite:///./auth.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    tablename = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "buyer" | "seller"

Base.metadata.create_all(bind=engine)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ── 2. Схемы ───────────────────────────────────────────────────────────
class LoginReq(BaseModel):
    username: str
    password: str

class RegisterReq(BaseModel):
    username: str
    password: str
    role: str

class AuthResp(BaseModel):
    success: bool
    role: Optional[str] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None

# ── 3. Класс сервиса (то, что ты просил) ───────────────────────────────
class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, password: str, role: str) -> AuthResp:
        if self.db.query(User).filter(User.username == username).first():
            return AuthResp(success=False, error="Пользователь уже существует")
        
        self.db.add(User(
            username=username,
            hashed_password=pwd_ctx.hash(password),
            role=role
        ))
        self.db.commit()
        return AuthResp(success=True, role=role)

    def login(self, username: str, password: str) -> AuthResp:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not pwd_ctx.verify(password, user.hashed_password):
            return AuthResp(
                success=False,
                error="Неверный логин или пароль",
                suggestion="Нет аккаунта? Зарегистрируйтесь."
            )
        return AuthResp(success=True, role=user.role)

# DI-фабрика
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# ── 4. Эндпоинты (только маршрутизация + валидация) ───────────────────
@app.post("/register", response_model=AuthResp)
def register(req: RegisterReq, svc: AuthService = Depends(get_auth_service)):
    return svc.register(req.username, req.password, req.role)

@app.post("/login", response_model=AuthResp)
def login(req: LoginReq, svc: AuthService = Depends(get_auth_service)):
    return svc.login(req.username, req.password)