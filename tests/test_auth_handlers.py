import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import timedelta

try:
    from auth_handlers import registerUser, loginUser
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from auth_handlers import registerUser, loginUser

@pytest.fixture
def mock_users_collection():
    return MagicMock()

@pytest.fixture
def mock_passlib_fixture():
    with patch('auth_handlers.pwd_context.hash', return_value='hashed_password'), \
         patch('auth_handlers.pwd_context.verify', return_value=True) as mock_verify:
        class Fixture:
            pass
        fixture = Fixture()
        fixture.MOCK_HASH = '$2b$12$R3fG8hJkLpQ9sW2vXyZ0Au.NlO4pQrStUvWxYzAbCdEfGhIjKlMn.'
        fixture.verify_return_value = mock_verify.return_value
        yield fixture

@patch('auth_handlers.get_users_collection')
@patch('auth_handlers.get_password_hash', return_value='mock_hashed_password')
def test_register_user_success(mock_get_hash, mock_get_users, mock_users):
    mock_get_users.return_value = mock_users
    mock_users.find_one.return_value = None
    mock_users.insert_one.return_value = MagicMock(inserted_id='mock_user_id')
    event = {'body': json.dumps({'email':'test@example.com','password':'password123'})}
    res = registerUser(event, {})
    assert res['statusCode']==201
    mock_users.insert_one.assert_called_once()
    args, _ = mock_users.insert_one.call_args
    assert args[0]['email']=='test@example.com'
    assert args[0]['hashedPassword']== 'mock_hashed_password'
    mock_get_hash.assert_called_once_with('password123')

@patch('auth_handlers.get_users_collection')
def test_register_user_existing_email(mock_get, mock_users):
    from pymongo.errors import DuplicateKeyError
    mock_get.return_value = mock_users
    mock_users.insert_one.side_effect = DuplicateKeyError('exists')
    event = {'body': json.dumps({'email':'exists@example.com','password':'pw'})}
    res = registerUser(event, {})
    assert res['statusCode']==400
    body=json.loads(res['body'])
    assert 'Email already registered' in body['message']

@patch('auth_handlers.get_users_collection')
@patch('auth_handlers.verify_password', return_value=True)
@patch('auth_handlers.create_access_token', return_value='mock_token')
def test_login_user_success(mock_create_token, mock_verify, mock_get_users, mock_users):
    mock_get_users.return_value = mock_users
    mock_users.find_one.return_value = {'_id':'user_id_123','email':'test','hashedPassword':'some_hash'}
    event={'body': json.dumps({'email':'test','password':'pw'})}
    res = loginUser(event,{})
    assert res['statusCode']==200
    body=json.loads(res['body'])
    assert body['token']=='mock_token'
    mock_verify.assert_called_once_with('pw', 'some_hash')
    mock_create_token.assert_called_once_with(data={'sub': 'user_id_123'}, expires_delta=timedelta(hours=1))

@patch('auth_handlers.get_users_collection')
@patch('auth_handlers.verify_password', return_value=False)
def test_login_user_invalid(mock_verify, mock_get_users, mock_users):
    mock_get_users.return_value = mock_users
    mock_users.find_one.return_value = {'_id':'id','email':'test','hashedPassword':'some_hash'}
    event={'body': json.dumps({'email':'test','password':'wrong'})}
    res = loginUser(event,{})
    assert res['statusCode']==401
    mock_verify.assert_called_once_with('wrong', 'some_hash')

@patch('auth_handlers.get_users_collection')
def test_login_user_not_found(mock_get, mock_users):
    mock_get.return_value = mock_users
    mock_users.find_one.return_value = None
    event={'body': json.dumps({'email':'no','password':'pw'})}
    res = loginUser(event,{})
    assert res['statusCode']==401
