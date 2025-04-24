from typing import Any, Dict, Optional, List
import json
import uuid
import time
from bson import ObjectId
from bson.errors import InvalidId
from db import get_tasks_collection

# Assume verify_token is implemented elsewhere and imported here
from auth_handlers import verify_token

def create_response(status_code: int, body: Any) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "body": json.dumps(body, default=str)
    }

def createTask(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id: Optional[str] = verify_token(event)
    if not user_id:
        return create_response(401, {"error": "Unauthorized"})

    try:
        body: Dict[str, Any] = json.loads(event.get('body', '{}'))
        title: Optional[str] = body.get('title')
        description: str = body.get('description', '')

        if not title:
            return create_response(400, {"error": "Title is required"})

        tasks_collection = get_tasks_collection()
        new_task: Dict[str, Any] = {
            "_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "status": "TODO",
            "createdAt": time.time(),
            "updatedAt": time.time(),
            "userId": user_id
        }
        result = tasks_collection.insert_one(new_task)

        created_task = tasks_collection.find_one({"_id": new_task["_id"]})
        if not created_task:
            return create_response(500, {"error": "Failed to retrieve created task"})

        return create_response(201, created_task)

    except Exception as e:
        print(f"Error creating task: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def getTasks(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("getTasks • incoming headers ->", event.get("headers"))
    user_id: Optional[str] = verify_token(event)
    print("getTasks • verify_token returned ->", user_id)
    if not user_id:
        return create_response(401, {"error": "Unauthorized"})
    try:
        tasks_collection = get_tasks_collection()
        tasks: List[Dict[str, Any]] = list(tasks_collection.find({"userId": user_id}))
        return create_response(200, tasks)
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return create_response(500, {"error": "Internal Server Error"})


def updateTaskStatus(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id: Optional[str] = verify_token(event)
    if not user_id:
        return create_response(401, {"error": "Unauthorized"})
    try:
        params: Dict[str, Any] = event.get('pathParameters', {}) or {}
        task_id: Optional[str] = params.get('taskId')
        if not task_id:
            return create_response(400, {"error": "Task ID is required"})
        body: Dict[str, Any] = json.loads(event.get('body', '{}'))
        status: Optional[str] = body.get('status')
        if not status:
            return create_response(400, {"error": "Status is required"})

        tasks_collection = get_tasks_collection()
        result = tasks_collection.update_one(
            {"_id": task_id, "userId": user_id},
            {"$set": {"status": status, "updatedAt": time.time()}}
        )
        if result.modified_count == 0:
            return create_response(404, {"error": "Task not found"})

        updated_task = tasks_collection.find_one({"_id": task_id, "userId": user_id})
        return create_response(200, updated_task)
    except InvalidId as e:
        return create_response(400, {"error": "Invalid Task ID"})
    except Exception as e:
        print(f"Error updating task status: {e}")
        return create_response(500, {"error": "Internal Server Error"})


def deleteTask(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id: Optional[str] = verify_token(event)
    if not user_id:
        return create_response(401, {"error": "Unauthorized"})
    try:
        params: Dict[str, Any] = event.get('pathParameters', {}) or {}
        task_id: Optional[str] = params.get('taskId')
        if not task_id:
            return create_response(400, {"error": "Task ID is required"})

        tasks_collection = get_tasks_collection()
        result = tasks_collection.delete_one({"_id": task_id, "userId": user_id})
        if result.deleted_count == 0:
            return create_response(404, {"error": "Task not found"})
        return create_response(200, {"message": "Task deleted successfully"})
    except InvalidId as e:
        return create_response(400, {"error": "Invalid Task ID"})
    except Exception as e:
        print(f"Error deleting task: {e}")
        return create_response(500, {"error": "Internal Server Error"})