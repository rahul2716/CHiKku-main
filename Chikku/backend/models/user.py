import datetime
import bcrypt
from bson import ObjectId

class User:
    def __init__(self, db):
        self.collection = db.users
        
    def create_user(self, name, email, password):
        """Create a new user with hashed password"""
        # Check if user already exists
        if self.collection.find_one({"email": email}):
            return None
            
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        result = self.collection.insert_one(user)
        user["_id"] = result.inserted_id
        return user
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.collection.find_one({"email": email})
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def verify_password(self, stored_password, provided_password):
        """Verify the provided password against the stored hash"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
