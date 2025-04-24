"""
Simple script to verify MongoDB Atlas connection locally using your .env configuration.
"""
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os, sys
from pymongo import MongoClient
import certifi

def main() -> None:
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    user: str = os.getenv("MONGO_USER", "")
    pw:   str = os.getenv("MONGO_PASS", "")
    host: str = os.getenv("MONGO_HOST", "")

    if not (user and pw and host):
        print("Error: MONGO_USER, MONGO_PASS or MONGO_HOST missing in .env")
        sys.exit(1)

    user_enc: str = quote_plus(user)
    pw_enc:   str = quote_plus(pw)
    uri: str = (
        f"mongodb+srv://{user_enc}:{pw_enc}@{host}"
        "/task_manager_db?retryWrites=true"
        "&w=majority&appName=Cluster0"
    )

    # uri = "mongodb+srv://savg:strasse1992@cluster0.vm2zz6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client: MongoClient = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5_000
        )
        client.admin.command("ping")
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
