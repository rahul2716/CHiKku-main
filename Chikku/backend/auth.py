import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")

def generate_token(user_id):
    """Generate a JWT token for the user"""
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': str(user_id)
    }
    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm='HS256'
    )

def decode_token(token):
    """Decode the JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing', 'status': 'error'}), 401
        
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'error': 'Token is invalid or expired', 'status': 'error'}), 401
        
        # Add user_id to request
        request.user_id = user_id
        
        return f(*args, **kwargs)
    
    return decorated