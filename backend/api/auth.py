from flask import Blueprint, request, jsonify

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Mock database to store users (replace with a real database later)
users = []

# Signup Route
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Get JSON data from the request
    email = data.get('email')
    password = data.get('password')

    # Check if the user already exists
    if any(user['email'] == email for user in users):
        return jsonify({"message": "User already exists"}), 400

    # Add the new user to the mock database
    new_user = {"email": email, "password": password}
    users.append(new_user)

    return jsonify({"message": "User created successfully", "user": new_user}), 201

# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Find the user in the mock database
    user = next((user for user in users if user['email'] == email and user['password'] == password), None)

    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401