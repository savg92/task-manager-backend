# Add these imports to handler.py
import os
import jwt
from passlib.context import CryptContext
from db import get_users_collection, get_db # Add get_db if needed for explicit checks
from datetime import datetime, timedelta, timezone # For JWT expiration
import json
import uuid
import time

from handler import create_response

# --- Authentication Dependencies ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get("JWT_SECRET", "fallback-secret-key") # Use the secret from env

# --- Auth Utility Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60)): # Token expires in 1 hour
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

# --- Authentication Handlers ---
def registerUser(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return create_response(400, {"error": "Email and password are required"})
        # Add more validation (email format, password complexity) here if needed

        users_collection = get_users_collection()
        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return create_response(400, {"error": "Email already registered"})

        hashed_password = get_password_hash(password)
        new_user = {
            "_id": str(uuid.uuid4()), # Use UUID string for ID
            "email": email,
            "hashedPassword": hashed_password,
            "createdAt": time.time()
        }
        users_collection.insert_one(new_user)

        return create_response(201, {"message": "User registered successfully"})

    except Exception as e:
        print(f"Error registering user: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def loginUser(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return create_response(400, {"error": "Email and password are required"})

        users_collection = get_users_collection()
        user = users_collection.find_one({"email": email})

        if not user or not verify_password(password, user.get("hashedPassword")):
            return create_response(401, {"error": "Incorrect email or password"})

        # Create JWT token
        access_token_expires = timedelta(hours=1) # Token validity period
        access_token = create_access_token(
            data={"sub": user["_id"]}, expires_delta=access_token_expires # 'sub' is standard claim for subject (user ID)
        )

        return create_response(200, {"access_token": access_token, "token_type": "bearer"})

    except Exception as e:
        print(f"Error logging in user: {e}")
        return create_response(500, {"error": "Internal Server Error"})

# --- Token Verification Helper ---
def verify_token(event):
    auth_header = event.get('headers', {}).get('Authorization', None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return None # No valid header found

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None # Token payload invalid
        return user_id # Return user_id on success
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None # Or raise specific exception
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None # Or raise specific exception