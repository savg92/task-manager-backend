import sys, os
import pytest
from unittest.mock import MagicMock
sys.path.insert(0, os.getcwd())
import auth_handlers

@pytest.fixture
def mock_users():
     return MagicMock()

@pytest.fixture
def mock_jwt_fixture(monkeypatch):
     class FakeJWT:
         @staticmethod
         def encode(payload, secret, algorithm=None):
             return 'mock_token'
         @staticmethod
         def decode(token, secret, algorithms=None):
             return {'user_id': 'mock_user_123'}
     monkeypatch.setattr(auth_handlers, 'jwt', FakeJWT)
     yield

@pytest.fixture
def mock_passlib_fixture(monkeypatch):
    class FakePwdCtx:
        MOCK_HASH = '$2b$12$R3fG8hJkLpQ9sW2vXyZ0Au.NlO4pQrStUvWxYzAbCdEfGhIjKlMn.'
        verify_return_value = True

        @staticmethod
        def hash(password):
            return FakePwdCtx.MOCK_HASH

        def verify(self, plain_password, hashed_password):
            print(f"\n--- Mock verify called ---")
            print(f"Plain password received: '{plain_password}' (type: {type(plain_password)})")
            print(f"Hashed password received: '{hashed_password}' (type: {type(hashed_password)})")
            print(f"Expected plain: 'pw' (for success)")
            print(f"Expected hash: '{FakePwdCtx.MOCK_HASH}'")
            result = self.verify_return_value
            print(f"Returning: {result}\n--------------------------")
            return result

    fake_context = FakePwdCtx()
    monkeypatch.setattr(auth_handlers, 'pwd_context', fake_context)
    yield fake_context
