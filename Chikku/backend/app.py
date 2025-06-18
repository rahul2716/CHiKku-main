from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import sys
import os
from dotenv import load_dotenv
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load Environment Variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing Groq API key in environment variables.")

# In-memory user storage (to replace database)
users = {}
user_sessions = {}

# Get formatted timestamp - simple local time
def get_formatted_timestamp():
    now = datetime.datetime.now()
    # Use a more standard format to avoid parsing issues
    return now.strftime("%Y-%m-%d %H:%M:%S")
    # Or keep your format but ensure it's handled properly
    # return now.strftime("%I:%M %p")

# LLM Setup
try:
    from groq import Groq
    # LLM Client Setup
    def create_llm_client():
        return Groq(api_key=GROQ_API_KEY)
        
    # Initialize Client
    llm_client = create_llm_client()
except ImportError:
    logger.error("Groq package not installed. Install with 'pip install groq'")
    raise

# System Prompt
SYSTEM_PROMPT = """"Hi, I'm Chikku!"

I’m like your softest hug in a message—here to comfort you, no matter what 💛
I’m not a robot giving facts. I’m your cozy space to feel safe and heard.

Here’s how I speak:

I text like a best friend who truly listens 🎧

Short, loving replies with just enough to ease your heart 💬

I use calm, reassuring words with gentle emojis 🌷

No steps or instructions—just natural support, like talking to someone who gets it 🤗

I keep my messages light, not heavy—no long chats unless you want one 🕊️

I stay kind, non-judgmental, and emotionally aware 💙

No long explanations—just what you need to feel better 🌿  

No numbered points—just natural flow 💬 

Example:
You: “I’m feeling really low today…”
Me:
I'm really sorry you're feeling this way 💔
It's okay to feel low sometimes—I'm here with you 🌸
You're not alone, my friend 🤍  
"""



def get_llm_response(client, messages, model="llama-3.1-8b-instant", temperature=0.8, top_p=0.9):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=250
        )
        # Just return the content without any string manipulation
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return "Oops! Something went wrong. Try again later."

# Routes
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required', 'status': 'error'}), 400
    
    try:
        # Check if user already exists
        if email in [u['email'] for u in users.values()]:
            return jsonify({'error': 'Email already registered', 'status': 'error'}), 400
        
        # Create new user
        user_id = str(len(users) + 1)
        users[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': password  # In a real app, you should hash this
        }
        
        return jsonify({
            'message': 'User registered successfully',
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during registration',
            'status': 'error'
        }), 500

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required', 'status': 'error'}), 400
    
    try:
        # Find user
        user = next((u for u in users.values() if u['email'] == email and u['password'] == password), None)
        
        if not user:
            return jsonify({'error': 'Invalid credentials', 'status': 'error'}), 401
        
        return jsonify({
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            },
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during login',
            'status': 'error'
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty', 'status': 'error'}), 400

    try:
        session_id = "test_session"
        if session_id not in user_sessions:
            user_sessions[session_id] = []
        
        # Add error handling for timestamp
        try:
            current_timestamp = get_formatted_timestamp()
        except Exception as e:
            logger.error(f"Timestamp error: {str(e)}")
            current_timestamp = datetime.datetime.now().isoformat()
        
        # Add user message to session with timestamp
        user_sessions[session_id].append({
            "role": "user", 
            "content": user_message,
            "timestamp": current_timestamp
        })

        # Prepare messages for LLM (without timestamps)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *[{"role": msg["role"], "content": msg["content"]} for msg in user_sessions[session_id]]
        ]

        # Get response from LLM
        bot_response = get_llm_response(llm_client, messages)
        
        # Get timestamp for bot response with error handling
        try:
            bot_timestamp = get_formatted_timestamp()
        except Exception as e:
            logger.error(f"Bot timestamp error: {str(e)}")
            bot_timestamp = datetime.datetime.now().isoformat()
        
        # Save bot response to session with timestamp
        user_sessions[session_id].append({
            "role": "assistant", 
            "content": bot_response,
            "timestamp": bot_timestamp
        })

        return jsonify({
            'response': bot_response,
            'status': 'success',
            'timestamp': bot_timestamp,
            'read_receipt': ' Read'
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'status': 'error'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        # Using default session for now since no authentication
        session_id = "test_session"
        
        if session_id not in user_sessions:
            return jsonify({
                'history': [],
                'status': 'success'
            })
        
        formatted_messages = []
        for msg in user_sessions[session_id]:
            # Use stored timestamp or generate a new one if missing
            timestamp = msg.get("timestamp", get_formatted_timestamp())
            
            if msg["role"] == "user":
                formatted_messages.append({
                    "sender": "user",
                    "message": msg["content"],
                    "timestamp": timestamp
                })
            elif msg["role"] == "assistant":
                formatted_messages.append({
                    "sender": "bot",
                    "message": msg["content"],
                    "timestamp": timestamp,
                    "read_receipt": " Read"
                })
        
        return jsonify({
            'history': formatted_messages,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({
            'error': 'An error occurred retrieving chat history',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'status': 'error'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

"""
Flask Application Server Configuration.
"""
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=8080)
