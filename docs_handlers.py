"""
Handler for serving API documentation via AWS Lambda and HTTP API.
"""
import os
from typing import Any, Dict

def get_docs(event: Any, context: Any) -> Dict[str, Any]:
    """AWS Lambda handler to return the API docs HTML."""
    project_dir = os.path.dirname(__file__)
    docs_path = os.path.join(project_dir, 'docs', 'index.html')
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Documentation not available: {e}'
        }
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html
    }

def get_openapi(event: Any, context: Any) -> Dict[str, Any]:
    """AWS Lambda handler to return the raw OpenAPI YAML spec."""
    project_dir = os.path.dirname(__file__)
    spec_path = os.path.join(project_dir, 'docs', 'openapi.yaml')
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = f.read()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'OpenAPI spec not available: {e}'
        }
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/yaml'},
        'body': spec
    }
