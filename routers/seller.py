#страница продавца
from fastapi import APIRouter, Depends, HTTPException, Cookie, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from database import get_db
from pydantic import BaseModel
import os
import shutil

router = APIRouter(prefix="/seller", tags=["Продавец"])
templates = Jinja2Templates(directory="templates") if os.path.exists("templates") else None

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str = None

# Зависимость для проверки продавца
def get_current_seller(session_id: str = Cookie(None), db=Depends(get_db)):
    if not session_id:
        raise HTTPException(401, "Требуется авторизация")
    
    user = db.execute("SELECT * FROM users WHERE id = ?", (int(session_id),)).fetchone()
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    if user["role"] != "продавец":
        raise HTTPException(403, "Доступ только для продавцов")
    
    return user

@router.get("/dashboard")
def seller_dashboard(user=Depends(get_current_seller), db=Depends(get_db), request: Request = None):
    """Панель продавца - просмотр своих товаров"""
    products = db.execute(
        "SELECT * FROM products WHERE seller_id = ?",
        (user["id"],)
    ).fetchall()
    
    if templates and request:
        return templates.TemplateResponse("seller_dashboard.html", {
            "request": request,
            "products": products
        })
    
    return {"products": [dict(p) for p in products]}

@router.post("/product/add")
def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
    user=Depends(get_current_seller),
    db=Depends(get_db)
):
    """Добавление товара"""
    image_path = None
    
    # Сохраняем изображение если есть
    if image and image.filename:
        os.makedirs("static/img/uploads", exist_ok=True)
        file_path = f"static/img/uploads/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/static/img/uploads/{image.filename}"
    
    db.execute(
        "INSERT INTO products (name, description, price, image, seller_id) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, image_path, user["id"])
    )
    db.commit()
    
    return {"message": "Товар добавлен"}

@router.get("/product/edit/{product_id}")
def edit_product_page(product_id: int, user=Depends(get_current_seller), db=Depends(get_db), request: Request = None):
    """Страница редактирования товара"""
    product = db.execute(
        "SELECT * FROM products WHERE id = ? AND seller_id = ?",
        (product_id, user["id"])
    ).fetchone()
    
    if not product:
        raise HTTPException(404, "Товар не найден или недоступен")
    
    if templates and request:
        return templates.TemplateResponse("edit_product.html", {
            "request": request,
            "product": product
        })
    
    return dict(product)

@router.post("/product/edit/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    user=Depends(get_current_seller),
    db=Depends(get_db)
):
    """Обновление товара"""
    product = db.execute(
        "SELECT * FROM products WHERE id = ? AND seller_id = ?",
        (product_id, user["id"])
    ).fetchone()
    
    if not product:
        raise HTTPException(404, "Товар не найден")
    
    db.execute(
        "UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?",
        (name, description, price, product_id)
    )
    db.commit()
    
    return {"message": "Товар обновлён"}

@router.post("/product/delete/{product_id}")
def delete_product(product_id: int, user=Depends(get_current_seller), db=Depends(get_db)):
    """Удаление товара"""
    product = db.execute(
        "SELECT * FROM products WHERE id = ? AND seller_id = ?",
        (product_id, user["id"])
    ).fetchone()
    
    if not product:
        raise HTTPException(404, "Товар не найден")
    
    db.execute("DELETE FROM products WHERE id = ? AND seller_id = ?", (product_id, user["id"]))
    db.commit()
    
    return {"message": "Товар удалён"}

