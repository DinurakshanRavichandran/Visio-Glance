from flask import Blueprint, request, jsonify
from db.database import MySQLDatabase

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'database': 'medical_app',
    'user': 'root',
    'password': ''
}

# ✅ Register Route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        with MySQLDatabase(**db_config) as db:
            success, message = db.register_user(username, email, password)
            if success:
                return jsonify({"success": True, "message": message}), 201
            return jsonify({"success": False, "message": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        with MySQLDatabase(**db_config) as db:
            success, user_data = db.login_user(email, password)
            if success:
                return jsonify({"success": True, "user": user_data}), 200
            return jsonify({"success": False, "error": user_data.get("error", "Unknown error")}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fetch User Route
@auth_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        with MySQLDatabase(**db_config) as db:
            user = db.fetch_one("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            if user:
                return jsonify(user), 200
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Logout Route (Optional)
@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "User logged out successfully"}), 200