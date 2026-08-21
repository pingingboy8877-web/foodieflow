from flask import Blueprint, render_template, request, jsonify
from app.database import get_db
from app.auth import hash_password, check_password, generate_token, token_required

bp = Blueprint('main', __name__)

# --- Page Rendering Routes ---
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/cart.html')
def cart_page():
    return render_template('cart.html')

@bp.route('/account.html')
def account_page():
    return render_template('account.html')

@bp.route('/about.html')
def about_page():
    return render_template('about.html')

# --- REST API Endpoints ---
@bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    hashed_pw = hash_password(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (username, email, hashed_pw))
        conn.commit()
    except Exception:
        return jsonify({'message': 'User already exists'}), 400
    finally:
        conn.close()

    return jsonify({'message': 'Account registered successfully'}), 201

@bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(password, user['password']):
        token = generate_token(user['id'], user['username'], user['role'])
        return jsonify({
            'token': token,
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email'], 'role': user['role']}
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/api/menu', methods=['GET'])
def get_menu():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'menu': items})

@bp.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json() or {}
    total_amount = data.get('total_amount')
    items = data.get('items', [])

    if not total_amount or not items:
        return jsonify({'message': 'Order total and items are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (?, ?)", 
                   (current_user['user_id'], total_amount))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    return jsonify({'message': 'Order placed successfully', 'order_id': order_id}), 201

@bp.route('/api/orders/my-orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (current_user['user_id'],))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'orders': orders})
