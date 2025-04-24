import pytest
import json
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from handler import createTask, getTasks, updateTaskStatus, deleteTask, getTaskById
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from handler import createTask, getTasks, updateTaskStatus, deleteTask, getTaskById

MOCK_USER_ID = 'mock_user_123'
MOCK_TASK_ID_STR = '605c7d77b0ef4a1f7a1b2c3d'
MOCK_TASK_ID_OBJ = ObjectId(MOCK_TASK_ID_STR)

@pytest.fixture
def mock_tasks_collection():
    return MagicMock()

def make_event(body=None, path_params=None, user_id=MOCK_USER_ID):
    event = {'requestContext': {'authorizer': {'lambda': {'user_id': user_id}}},
             'body': json.dumps(body) if body is not None else '{}',
             'pathParameters': path_params or {}}
    return event

@patch('handler.get_tasks_collection')
def test_create_task(mock_get, mock_tasks_collection):
    mock_get.return_value = mock_tasks_collection
    mock_tasks_collection.insert_one.return_value = MagicMock(inserted_id=MOCK_TASK_ID_OBJ)

    data = {'title': 'Test', 'description': 'Desc'}
    res = createTask(make_event(body=data), {})
    assert res['statusCode'] == 201

@patch('handler.get_tasks_collection')
def test_get_tasks(mock_get, mock_tasks_collection):
    mock_get.return_value = mock_tasks_collection
    docs = [{'user_id': MOCK_USER_ID, '_id': ObjectId(), 'title': 'A', 'completed': False}]
    mock_tasks_collection.find.return_value = docs
    res = getTasks(make_event(), {})
    assert res['statusCode'] == 200

@patch('handler.get_tasks_collection')
def test_update_task_not_found(mock_get, mock_tasks_collection):
    mock_get.return_value = mock_tasks_collection
    mock_tasks_collection.update_one.return_value = MagicMock(modified_count=0)
    res = updateTaskStatus(make_event(body={'status': 'DONE'}, path_params={'taskId': 'non-existent-id'}), {})
    assert res['statusCode'] == 404

@patch('handler.get_tasks_collection')
def test_delete_task(mock_get, mock_tasks_collection):
    mock_get.return_value = mock_tasks_collection
    mock_tasks_collection.delete_one.return_value = MagicMock(deleted_count=1)
    res = deleteTask(make_event(path_params={'taskId': MOCK_TASK_ID_STR}), {})
    assert res['statusCode'] == 204

@patch('handler.get_tasks_collection')
def test_get_task_by_id(mock_get, mock_tasks_collection):
    mock_get.return_value = mock_tasks_collection
    mock_tasks_collection.find_one.return_value = {'_id': MOCK_TASK_ID_OBJ, 'user_id': MOCK_USER_ID, 'title': 'X', 'completed': False}
    res = getTaskById(make_event(path_params={'taskId': MOCK_TASK_ID_STR}), {})
    assert res['statusCode'] == 200
