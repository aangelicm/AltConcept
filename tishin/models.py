import sqlite3
from datetime import datetime

def get_connect():
    connection = sqlite3.connect("shop.bd")
    connection.row_factory = sqlite3.Row
    return connection

def database():
    conn = get_connect()
    cursor = conn.cursor()

    #таблица юзеры
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('покупатель', 'продавец'))
        )
    ''')

    #таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            image TEXT,
            seller_id INTEGER NOT NULL,
            FOREIGN KEY (seller_id) REFERNCES users (id)
        )
    ''')

    #таблица карзина
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERNCES users (id),
            FOREIGN KEY (product_id) REFERNCES products (id)           
        )
    ''')

    #таблица заказизазазазазааз
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERNCES users (id)
        )
    ''')
    conn.commit()