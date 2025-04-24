import os
from dotenv import load_dotenv
from typing import Final, Optional
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import certifi

# Load environment variables
load_dotenv()

# Build MongoDB URI from separate credentials
user: Final[str] = os.getenv("MONGO_USER", "")
pw:   Final[str] = os.getenv("MONGO_PASS", "")
host: Final[str] = os.getenv("MONGO_HOST", "")
if not (user and pw and host):
    raise RuntimeError("MONGO_USER, MONGO_PASS and MONGO_HOST must be set in .env")

user_enc: Final[str] = quote_plus(user)
pw_enc:   Final[str] = quote_plus(pw)
MONGO_URI: Final[str] = (
    f"mongodb+srv://{user_enc}:{pw_enc}@{host}"
    "/task_manager_db?retryWrites=true"
    "&w=majority&appName=Cluster0"
)

_client: Optional[MongoClient] = None
_db:     Optional[Database]    = None

def init_db() -> Database:
    global _client, _db
    if _client is None or _db is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5_000,
            tls=True,
            tlsCAFile=certifi.where(),
        )
        _client.admin.command("ping")
        _db = _client.get_database("task_manager_db")
        try:
            _db['users'].create_index("email", unique=True)
        except Exception:
            pass
    return _db

def get_db() -> Database:
    return init_db()

def get_tasks_collection() -> Collection:
    return init_db().get_collection("tasks")

def get_users_collection() -> Collection:
    return init_db().get_collection("users")