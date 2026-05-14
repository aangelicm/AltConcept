from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import init_db  # <-- Теперь здесь init_db
import os

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db() # <-- Вызываем нашу новую функцию

# ... остальной код main.py ...



