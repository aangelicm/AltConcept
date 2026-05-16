from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import init_db  
import os 

from routers.authorization import router as authorization_router
from routers.buyer import router as buyer_router
from routers.seller import router as seller_router


app = FastAPI()

# Подключаем папку static (картинки, css, js)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(authorization_router)
app.include_router(buyer_router)
app.include_router(seller_router)


@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "AltConcept API работает. Перейди на /auth/register или /auth/login"}






