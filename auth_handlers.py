import os
import jwt
from passlib.context import CryptContext
from db import get_users_collection, get_db
from datetime import datetime, timedelta, timezone
import json
import uuid
import time
from typing import Any, Dict, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get("JWT_SECRET", "fallback-secret-key")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: timedelta = timedelta(minutes=60),
) -> str:
    to_encode: Dict[str, Any] = data.copy()
    expire: datetime = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    encoded_jwt: str = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def registerUser(
    event: Dict[str, Any],
    context: Any
) -> Dict[str, Any]:
    from handler import create_response
    from pymongo.errors import DuplicateKeyError
    try:
        body: Dict[str, Any] = json.loads(event.get("body", "{}"))
        email: Optional[str] = body.get("email")
        password: Optional[str] = body.get("password")

        if not email or not password:
            return create_response(400, {"error": "Email and password are required"})

        users = get_users_collection()
        if users.find_one({"email": email}):
            return create_response(400, {"error": "Email already registered"})

        new_user: Dict[str, Any] = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "hashedPassword": get_password_hash(password),
            "createdAt": time.time(),
        }
        try:
            users.insert_one(new_user)
        except DuplicateKeyError:
            return create_response(400, {"error": "Email already registered"})
        return create_response(201, {"message": "User registered successfully"})

    except Exception as e:
        print(f"Error registering user: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def loginUser(
    event: Dict[str, Any],
    context: Any
) -> Dict[str, Any]:
    from handler import create_response
    try:
        body: Dict[str, Any] = json.loads(event.get("body", "{}"))
        email: Optional[str] = body.get("email")
        password: Optional[str] = body.get("password")

        if not email or not password:
            return create_response(400, {"error": "Email and password are required"})

        users = get_users_collection()
        user: Optional[Dict[str, Any]] = users.find_one({"email": email})
        hashed = user.get("hashedPassword") or user.get("password") if user else None
        if not user or not verify_password(password, hashed or ""):
            return create_response(401, {"error": "Incorrect email or password"})

        token: str = create_access_token(
            data={"sub": user["_id"]},
            expires_delta=timedelta(hours=1),
        )
        return create_response(200, {"token": token})

    except Exception as e:
        print(f"Error logging in user: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def verify_token(event: Dict[str, Any]) -> Optional[str]:
    """
    Extracts and verifies a Bearer JWT from the Lambda event.
    Returns the `sub` claim (user_id) on success, or None on failure.
    """
    print("verify_token: event.headers ->", event.get("headers"))
    headers = event.get("headers")
    if not isinstance(headers, dict):
        print("verify_token: missing headers or wrong type")
        return None

    auth_header = headers.get("Authorization") or headers.get("authorization")
    print("verify_token: raw auth_header ->", auth_header)
    if not isinstance(auth_header, str) or not auth_header.startswith("Bearer "):
        print("verify_token: malformed or missing Bearer token")
        return None

    token = auth_header.split(" ", 1)[1]
    try:
        payload: Dict[str, Any] = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print("verify_token: decoded payload ->", payload)
        sub = payload.get("sub")
        if not isinstance(sub, str):
            print("verify_token: sub claim missing or not a string")
            return None
        return sub
    except jwt.ExpiredSignatureError:
        print("verify_token: token expired")
        return None
    except jwt.InvalidTokenError as e:
        print("verify_token: invalid token ->", str(e))
        return None