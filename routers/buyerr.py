#страница покупателя
from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
from fastapi.templating import Jinja2Templates
from database import get_db
import os

router = APIRouter(prefix="/buyer", tags=["Покупатель"])
templates = Jinja2Templates(directory="templates") if os.path.exists("templates") else None

# Зависимость для проверки авторизации
def get_current_buyer(session_id: str = Cookie(None), db=Depends(get_db)):
    if not session_id:
        raise HTTPException(401, "Требуется авторизация")
    
    user = db.execute("SELECT * FROM users WHERE id = ?", (int(session_id),)).fetchone()
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    if user["role"] != "покупатель":
        raise HTTPException(403, "Доступ только для покупателей")
    
    return user

@router.get("/catalog")
def view_catalog(request: Request, db=Depends(get_db)):
    """Просмотр всех товаров"""
    products = db.execute("SELECT * FROM products").fetchall()
    
    if templates:
        return templates.TemplateResponse("catalog.html", {
            "request": request,
            "products": products
        })
    return {"products": [dict(p) for p in products]}

@router.get("/product/{product_id}")
def view_product(product_id: int, request: Request, db=Depends(get_db)):
    """Просмотр конкретного товара"""
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        raise HTTPException(404, "Товар не найден")
    
    if templates:
        return templates.TemplateResponse("product.html", {
            "request": request,
            "product": product
        })
    return dict(product)

@router.get("/cart")
def view_cart(user=Depends(get_current_buyer), db=Depends(get_db)):
    """Просмотр корзины"""
    items = db.execute('''
        SELECT c.*, p.name, p.price, p.image 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (user["id"],)).fetchall()
    
    total = sum(item["price"] * item["quantity"] for item in items)
    
    return {"items": [dict(i) for i in items], "total": total}

@router.post("/cart/add/{product_id}")
def add_to_cart(product_id: int, quantity: int = 1, user=Depends(get_current_buyer), db=Depends(get_db)):
    """Добавить товар в корзину"""
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        raise HTTPException(404, "Товар не найден")
    
    # Проверяем, есть ли уже в корзине
    existing = db.execute(
        "SELECT * FROM cart WHERE user_id = ? AND product_id = ?",
        (user["id"], product_id)
    ).fetchone()
    
    if existing:
        db.execute(
            "UPDATE cart SET quantity = quantity + ? WHERE id = ?",
            (quantity, existing["id"])
        )
    else:
        db.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user["id"], product_id, quantity)
        )
    
    db.commit()
    return {"message": "Товар добавлен в корзину"}

@router.post("/cart/remove/{product_id}")
def remove_from_cart(product_id: int, user=Depends(get_current_buyer), db=Depends(get_db)):
    """Удалить товар из корзины"""
    db.execute(
        "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
        (user["id"], product_id)
    )
    db.commit()
    return {"message": "Товар удалён из корзины"}

@router.post("/checkout")
def checkout(user=Depends(get_current_buyer), db=Depends(get_db)):
    """Оформление заказа"""
    items = db.execute('''
        SELECT c.*, p.price 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (user["id"],)).fetchall()
    
    if not items:
        raise HTTPException(400, "Корзина пуста")
    
    total = sum(item["price"] * item["quantity"] for item in items)
    
    # Создаём заказ
    db.execute(
        "INSERT INTO orders (user_id, total_price) VALUES (?, ?)",
        (user["id"], total)
    )
    db.commit()
    
    # Очищаем корзину
    db.execute("DELETE FROM cart WHERE user_id = ?", (user["id"],))
    db.commit()
    
    return {"message": "Заказ оформлен", "total": total}

