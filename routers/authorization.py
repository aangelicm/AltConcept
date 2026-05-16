# from fastapi import FastAPI, Form
# import sqlite3
# #создаю приложение фаст апи

# app = FastAPI()
# @app.post("/redister") #отправляю данные на сервер 

# def redister(username: str = Form(...), password: str = Form(...)):
#     connection = sqlite3.connect("shpp.bd")
#     cursor = connection.cursor()

#     cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#     connection.commit()
#     return {"message": "все крута"}

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from database import get_db
from pydantic import BaseModel
import sqlite3
import os

router = APIRouter(prefix="/auth", tags=["Авторизация"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates") if os.path.exists("templates") else None

class UserForm(BaseModel):
    username: str
    password: str
    role: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@router.get("/register")
def register_page(request: Request):
    if templates:
        return templates.TemplateResponse("register.html", {"request": request})
    return {"page": "register"}

@router.post("/register")
def register(username: str, password: str, role: str, db=Depends(get_db)):
    if role not in ['покупатель', 'продавец']:
        raise HTTPException(400, "Неверная роль")
    
    try:
        hashed = hash_password(password)
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, hashed, role))
        db.commit()
        return {"message": "Регистрация успешна"}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Пользователь уже существует")

@router.get("/login")
def login_page(request: Request):
    if templates:
        return templates.TemplateResponse("login.html", {"request": request})
    return {"page": "login"}

@router.post("/login")
def login(username: str, password: str, response: Response, db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(401, "Неверный логин или пароль")
    
    # Сохраняем сессию в cookie
    response.set_cookie(
        key="session_id",
        value=str(user["id"]),
        httponly=True,
        samesite="lax",
        max_age=86400  # 24 часа
    )
    
    return {"message": "Вход выполнен", "role": user["role"], "user_id": user["id"]}

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("session_id")
    return {"message": "Выход выполнен"}

@router.get("/me")
def get_current_user(session_id: str = Cookie(None), db=Depends(get_db)):
    if not session_id:
        raise HTTPException(401, "Не авторизован")
    
    user = db.execute("SELECT id, username, role FROM users WHERE id = ?", 
                      (int(session_id),)).fetchone()
    if not user:
        raise HTTPException(401, "Сессия недействительна")
    
    return {"user_id": user["id"], "username": user["username"], "role": user["role"]}


