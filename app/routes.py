from flask import Blueprint, jsonify, render_template, request
from app.auth import check_password, generate_token, hash_password, token_required
from app.database import get_db

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/cart.html")
def cart_page():
    return render_template("cart.html")

@bp.route("/account.html")
def account_page():
    return render_template("account.html")

@bp.route("/about.html")
def about_page():
    return render_template("about.html")

@bp.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "FoodieFlow API"})

@bp.get("/api/menu")
def get_menu():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    conn = get_db()
    query = "SELECT * FROM menu WHERE available = 1"
    params = []

    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY featured DESC, id DESC"
    items = [dict(row) for row in conn.execute(query, params).fetchall()]
    conn.close()
    return jsonify({"menu": items})

@bp.get("/api/categories")
def categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM menu WHERE available = 1 ORDER BY category").fetchall()
    conn.close()
    return jsonify({"categories": [row["category"] for row in rows]})

@bp.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(username) < 3 or "@" not in email or len(password) < 8:
        return jsonify({"message": "Use a username, valid email and password of at least 8 characters."}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hash_password(password))
        )
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"message": "Username or email is already registered."}), 409
    conn.close()
    return jsonify({"message": "Account created successfully."}), 201

@bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    identity = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (identity, identity.lower())
    ).fetchone()
    conn.close()

    if not user or not check_password(password, user["password"]):
        return jsonify({"message": "Invalid login details."}), 401

    token = generate_token(user["id"], user["username"], user["role"])
    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    })

@bp.post("/api/orders")
@token_required
def create_order(current_user):
    data = request.get_json(silent=True) or {}
    raw_items = data.get("items", [])
    address = str(data.get("delivery_address", "")).strip()

    if not raw_items or not address:
        return jsonify({"message": "Cart items and delivery address are required."}), 400

    requested = {}
    try:
        for item in raw_items:
            menu_id = int(item["id"])
            qty = max(1, min(20, int(item.get("quantity", 1))))
            requested[menu_id] = requested.get(menu_id, 0) + qty
    except (KeyError, TypeError, ValueError):
        return jsonify({"message": "Invalid cart data."}), 400

    conn = get_db()
    ids = list(requested.keys())
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"SELECT id, price FROM menu WHERE id IN ({placeholders}) AND available = 1", ids
    ).fetchall()

    if len(rows) != len(ids):
        conn.close()
        return jsonify({"message": "One or more menu items are no longer available."}), 409

    prices = {row["id"]: float(row["price"]) for row in rows}
    subtotal = sum(prices[item_id] * qty for item_id, qty in requested.items())
    delivery_fee = 1500 if subtotal < 15000 else 0
    total = subtotal + delivery_fee

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, total_amount, delivery_fee, delivery_address) VALUES (?, ?, ?, ?)",
        (current_user["user_id"], total, delivery_fee, address)
    )
    order_id = cur.lastrowid

    for menu_id, qty in requested.items():
        cur.execute(
            "INSERT INTO order_items (order_id, menu_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, menu_id, qty, prices[menu_id])
        )

    conn.commit()
    conn.close()
    return jsonify({
        "message": "Order placed successfully.",
        "order_id": order_id,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total
    }), 201

@bp.get("/api/orders/my-orders")
@token_required
def get_user_orders(current_user):
    conn = get_db()
    orders = [dict(row) for row in conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (current_user["user_id"],)
    ).fetchall()]
    conn.close()
    return jsonify({"orders": orders})
