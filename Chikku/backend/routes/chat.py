from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import ChatDatabase

chat_bp = Blueprint('chat', __name__)
db = ChatDatabase()

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user_message = data.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    # Here you would process the message with your chatbot logic
    # For now, let's just echo the message back
    bot_response = f"Echo: {user_message}"
    
    # Store the chat in the database
    success = db.store_chat(user_id, user_message, bot_response)
    if not success:
        return jsonify({"error": "Failed to store chat message"}), 500
    
    return jsonify({
        "response": bot_response
    }), 200

@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=50, type=int)
    
    history = db.get_user_chat_history(user_id, limit)
    
    return jsonify({
        "history": history
    }), 200

@chat_bp.route('/search', methods=['GET'])
@jwt_required()
def search_chats():
    search_term = request.args.get('q')
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400
    
    limit = request.args.get('limit', default=20, type=int)
    
    results = db.search_chats(search_term, limit)
    
    return jsonify({
        "results": results
    }), 200
