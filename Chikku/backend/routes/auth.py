from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
import datetime
from database import ChatDatabase

auth_bp = Blueprint('auth', __name__)
db = ChatDatabase()

# Assuming you have a blacklist collection in your database to store revoked tokens
# Let's add this to the database.py first

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    if not db.verify_password(user['password'], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Create access token
    access_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=datetime.timedelta(days=1)
    )
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": str(user['_id']),
            "name": user['name'],
            "email": user['email']
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the JWT ID
    user_id = get_jwt_identity()
    
    # Add the token to the blacklist
    db.add_to_blacklist(jti)
    
    return jsonify({"message": "Successfully logged out"}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    # Check if user already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    # Create new user
    user = db.create_user(name, email, password)
    if not user:
        return jsonify({"error": "Failed to create user"}), 500
    
    # Create JWT token
    access_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=timedelta(days=1)
    )
    
    # Remove password from user object before sending to client
    user_data = {k: v for k, v in user.items() if k != 'password'}
    # Convert ObjectId to string for JSON serialization
    if '_id' in user_data:
        user_data['_id'] = str(user_data['_id'])
    
    return jsonify({
        "token": access_token,
        "user": user_data
    }), 201
