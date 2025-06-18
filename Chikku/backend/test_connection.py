from database import ChatDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    try:
        # Initialize database
        db = ChatDatabase()
        
        # Test connection
        if db.is_connected():
            logger.info("Successfully connected to MongoDB!")
            
            # Test storing a message
            test_message = {
                'user_id': 'test_user',
                'user_message': 'Test message',
                'bot_response': 'Test response'
            }
            
            # Store test message
            db.store_chat(**test_message)
            logger.info("Successfully stored test message")
            
            # Retrieve test message
            history = db.get_user_chat_history('test_user', limit=1)
            logger.info(f"Retrieved {len(history)} messages")
            
            if history:
                logger.info("Test successful! MongoDB is working correctly")
                return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
