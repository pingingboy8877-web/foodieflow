import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("FOODIE_DB_PATH", BASE_DIR / "foodie.db"))

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        price REAL NOT NULL,
        category TEXT NOT NULL,
        image_url TEXT,
        featured INTEGER DEFAULT 0,
        available INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        delivery_fee REAL DEFAULT 0,
        status TEXT DEFAULT 'pending',
        delivery_address TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (menu_id) REFERENCES menu(id)
    );
    """)

    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        items = [
            ("Smoky Suya Burger", "Char-grilled beef, suya spice, onions and house sauce.", 6500, "Burgers", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=85", 1),
            ("Jollof Rice & Chicken", "Party-style jollof, smoky grilled chicken and fresh slaw.", 7800, "Rice", "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?auto=format&fit=crop&w=900&q=85", 1),
            ("Peppered Chicken", "Tender chicken tossed in a rich Nigerian pepper sauce.", 7200, "Chicken", "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=900&q=85", 1),
            ("Crispy Plantain", "Golden sweet plantain with a light chilli seasoning.", 2800, "Sides", "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85", 0),
            ("Prawn Pasta", "Creamy pasta, garlic, herbs and seasoned prawns.", 9500, "Pasta", "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?auto=format&fit=crop&w=900&q=85", 1),
            ("Mango Chill", "Fresh mango, citrus and ice blended to order.", 3500, "Drinks", "https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=900&q=85", 0),
        ]
        cur.executemany(
            "INSERT INTO menu (name, description, price, category, image_url, featured) VALUES (?, ?, ?, ?, ?, ?)",
            items
        )

    conn.commit()
    conn.close()
