import sqlite3
import os

DB_PATH = "/tmp/foodie.db" if os.environ.get("VERCEL") else "foodie.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer'
        )
    ''')
    
    # Menu Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT
        )
    ''')

    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert Initial Menu items if empty
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        sample_menu = [
            ("Suya Spiced Burger", 12.50, "Mains", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"),
            ("Jollof Rice Bowl", 10.00, "Mains", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400"),
            ("Crispy Plantain Fries", 4.50, "Sides", "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=400"),
            ("Tropical Mango Smoothie", 5.00, "Drinks", "https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400")
        ]
        cursor.executemany("INSERT INTO menu (name, price, category, image_url) VALUES (?, ?, ?, ?)", sample_menu)
        
    conn.commit()
    conn.close()
