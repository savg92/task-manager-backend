import pytest
from unittest.mock import patch, mock_open

try:
    from docs_handlers import get_docs, get_openapi
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from docs_handlers import get_docs, get_openapi

@patch("builtins.open", new_callable=mock_open, read_data="<html>Mock Docs</html>")
@patch("os.path.dirname", return_value="/mock/project/dir")
def test_get_docs_success(mock_dirname, mock_file):
    event = {}
    context = {}
    response = get_docs(event, context)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "text/html"
    assert response["body"] == "<html>Mock Docs</html>"
    mock_file.assert_called_once_with("/mock/project/dir/docs/index.html", 'r', encoding='utf-8')

@patch("builtins.open", side_effect=FileNotFoundError("Docs file not found"))
@patch("os.path.dirname", return_value="/mock/project/dir")
def test_get_docs_file_not_found(mock_dirname, mock_file):
    event = {}
    context = {}
    response = get_docs(event, context)
    assert response["statusCode"] == 500
    assert "Documentation not available" in response["body"]
    assert "Docs file not found" in response["body"]

@patch("builtins.open", new_callable=mock_open, read_data="openapi: 3.1.0")
@patch("os.path.dirname", return_value="/mock/project/dir")
def test_get_openapi_success(mock_dirname, mock_file):
    event = {}
    context = {}
    response = get_openapi(event, context)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/yaml"
    assert response["body"] == "openapi: 3.1.0"
    mock_file.assert_called_once_with("/mock/project/dir/docs/openapi.yaml", 'r', encoding='utf-8')

@patch("builtins.open", side_effect=FileNotFoundError("Spec file not found"))
@patch("os.path.dirname", return_value="/mock/project/dir")
def test_get_openapi_file_not_found(mock_dirname, mock_file):
    event = {}
    context = {}
    response = get_openapi(event, context)
    assert response["statusCode"] == 500
    assert "OpenAPI spec not available" in response["body"]
    assert "Spec file not found" in response["body"]
