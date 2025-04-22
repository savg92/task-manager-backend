from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

client: Optional[MongoClient] = None
db: Optional[Database] = None
tasks_collection: Optional[Collection] = None
users_collection: Optional[Collection] = None

try:
    print("Attempting to connect to MongoDB...")
    client = MongoClient(settings.MONGO_URI)
    client.admin.command('ismaster')
    db = client.get_database("task_manager_db")
    print("MongoDB connection successful.")
    tasks_collection = db['tasks']
    users_collection = db['users']
except ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")
except Exception as e:
    print(f"An error occurred during MongoDB setup: {e}")

def get_db() -> Database:
    if db is None:
        raise Exception("Database not initialized")
    return db

def get_tasks_collection() -> Collection:
    return get_db()['tasks']

def get_users_collection() -> Collection:
    return get_db()['users']

if users_collection is not None:
    try:
        users_collection.create_index("email", unique=True)
        print("User email index created.")
    except Exception as e:
        print(f"Could not create user email index (might already exist): {e}")