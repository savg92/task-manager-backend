import json
import uuid
import time
from bson import ObjectId # Import ObjectId
from bson.errors import InvalidId # Import InvalidId for error handling
from db import get_tasks_collection # Assuming db.py is in the same directory

# --- Helper Function for Responses ---
def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            # Required for CORS support to work with httpApi
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(body, default=str) # Use default=str to handle ObjectId
    }

# --- Task Functions (No Auth Yet) ---
def createTask(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        description = body.get('description', '') # Optional description

        if not title:
            return create_response(400, {"error": "Title is required"})

        tasks_collection = get_tasks_collection()
        new_task = {
            "_id": str(uuid.uuid4()), # Use UUID string for ID
            "title": title,
            "description": description,
            "status": "TODO", # Default status
            "createdAt": time.time(),
            "updatedAt": time.time()
            # "userId": "..." # Add this later with authentication
        }
        result = tasks_collection.insert_one(new_task)

        # Fetch the inserted document to return it
        created_task = tasks_collection.find_one({"_id": new_task["_id"]})
        if not created_task:
             return create_response(500, {"error": "Failed to retrieve created task"})

        return create_response(201, created_task)

    except Exception as e:
        print(f"Error creating task: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def getTasks(event, context):
    try:
        tasks_collection = get_tasks_collection()
        # Later, filter by userId: tasks = list(tasks_collection.find({"userId": userId}))
        tasks = list(tasks_collection.find())
        return create_response(200, tasks)
    except Exception as e:
        print(f"Error getting tasks: {e}")
        return create_response(500, {"error": "Internal Server Error"})

def updateTaskStatus(event, context):
    try:
        task_id = event['pathParameters'].get('taskId')
        if not task_id: # Basic check
             return create_response(400, {"error": "Task ID is required in path"})

        body = json.loads(event.get('body', '{}'))
        status = body.get('status')
        valid_statuses = ["TODO", "IN_PROGRESS", "COMPLETED"]

        if not status or status not in valid_statuses:
            return create_response(400, {"error": f"Invalid status provided. Must be one of {valid_statuses}"})

        tasks_collection = get_tasks_collection()

        # Later, add userId to the filter: {"_id": task_id, "userId": userId}
        result = tasks_collection.update_one(
            {"_id": task_id},
            {"$set": {"status": status, "updatedAt": time.time()}}
        )

        if result.matched_count == 0:
            return create_response(404, {"error": "Task not found"})
        if result.modified_count == 0:
             return create_response(200, {"message": "Task status was already set to the provided value."}) # Or 304 Not Modified? 200 is simpler.


        # Fetch the updated document to return it
        updated_task = tasks_collection.find_one({"_id": task_id})
        if not updated_task:
             return create_response(404, {"error": "Task not found after update attempt"}) # Should not happen if matched_count > 0

        return create_response(200, updated_task)

    except Exception as e:
        print(f"Error updating task status: {e}")
        return create_response(500, {"error": "Internal Server Error"})


def deleteTask(event, context):
    try:
        task_id = event['pathParameters'].get('taskId')
        if not task_id:
             return create_response(400, {"error": "Task ID is required in path"})

        tasks_collection = get_tasks_collection()

        # Later, add userId to the filter: {"_id": task_id, "userId": userId}
        result = tasks_collection.delete_one({"_id": task_id})

        if result.deleted_count == 0:
            return create_response(404, {"error": "Task not found"})

        return create_response(200, {"message": "Task deleted successfully"}) # 204 No Content is also valid, but harder to confirm in testing/UI

    except Exception as e:
        print(f"Error deleting task: {e}")
        return create_response(500, {"error": "Internal Server Error"})

# Keep the hello function from template or remove if not needed
def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }
    return create_response(200, body)