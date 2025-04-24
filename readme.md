# Task Manager Backend

A serverless backend for managing user tasks, built with AWS Lambda, Python 3.12, and the Serverless Framework. This service provides user registration, authentication, and full CRUD operations on tasks.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Local Testing](#local-testing)
  - [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- User registration and login (JWT-based authentication)
- Create, read, update, and delete tasks
- Serverless deployment on AWS Lambda with HTTP API Gateway
- Environment-based configuration with dotenv

## Prerequisites
- Node.js >= 16
- Python 3.12
- Docker (for building Python dependencies)
- AWS CLI configured with appropriate IAM permissions
- [Serverless Framework CLI](https://www.serverless.com/) installed globally:

  ```zsh
  npm install -g serverless
  ```

## Installation
1. Clone the repo:
   ```zsh
   git clone https://github.com/savg92/task-manager-backend
   cd task-manager-backend
   ```
2. Install NPM dev dependencies:
   ```zsh
   npm install
   ```
3. Install Python runtime dependencies (you can use a virtual environment):
   ```zsh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Configuration
- Copy the `.env.example` file in the project root to `.env` and fill in your values:
```dotenv
# MongoDB Atlas connection details
MONGO_USER="<db_username>"
MONGO_PASS="<db_password>"
MONGO_HOST="<cluster_host>"

# JWT secret for token signing
JWT_SECRET="<your_jwt_secret>"
```

The Serverless Framework will automatically load these values.

## Usage

### Local Testing

You can test individual functions locally:

```zsh
# Test database connection
python test_db_connection.py

# Invoke a Lambda handler locally (example: getTasks)
serverless invoke local -f getTasks --path sample_event.json
```

### Deployment

Deploy to AWS:

```zsh
serverless deploy -v
```

After deployment, you'll receive HTTP endpoints for all functions.

## API Endpoints

| Method | Path                      | Description                          |
| ------ | ------------------------- | ------------------------------------ |
| POST   | /register                 | Register a new user                 |
| POST   | /login                    | Authenticate and receive a JWT       |
| POST   | /tasks                    | Create a new task (authenticated)    |
| GET    | /tasks                    | Fetch all tasks for the user         |
| GET    | /tasks/{taskId}           | Fetch a single task by ID            |
| PUT    | /tasks/{taskId}/status    | Update task status (authenticated)   |
| DELETE | /tasks/{taskId}           | Delete a task (authenticated)        |
| GET    | /docs                     | Serve static HTML API documentation  |
| GET    | /openapi.yaml             | Serve the raw OpenAPI specification  |

All routes requiring authentication (`/tasks` and sub-routes) need an `Authorization: Bearer <token>` header obtained from the `/login` endpoint.

## Testing

- **Database Connection:** Verify access to MongoDB:
  ```zsh
  python test_db_connection.py
  ```
- **Unit Tests:** Run the unit test suite using `pytest`:
  ```zsh
  pytest -v tests/
  ```

## Documentation
- Raw OpenAPI spec: [`docs/openapi.yaml`](docs/openapi.yaml)
- Static HTML docs: [`docs/index.html`](docs/index.html) (open directly in your browser)
- Interactive docs (local): run `python open_docs.py` to serve and open docs at http://localhost:8000
- Deployed docs: [https://ngte2hwp1k.execute-api.us-east-1.amazonaws.com/docs](https://ngte2hwp1k.execute-api.us-east-1.amazonaws.com/docs)
- Swagger UI: [Swagger Editor](https://editor.swagger.io/) (paste the OpenAPI spec)

## Project Structure
```
.
├── auth_handlers.py        # User registration & login logic
├── db.py                   # MongoDB client setup
├── docs_handlers.py        # Handlers for serving API docs
├── handler.py              # Task CRUD handlers
├── open_docs.py            # Script to serve docs locally
├── package.json            # NPM dev dependencies (Serverless plugins)
├── readme.md               # This file
├── requirements.txt        # Python runtime dependencies
├── serverless.yml          # Serverless service configuration
├── test_db_connection.py   # DB connection test script
├── docs/
│   ├── index.html          # Static HTML documentation page
│   └── openapi.yaml        # OpenAPI 3.x specification
└── tests/
    ├── __init__.py
    ├── conftest.py         # Pytest fixtures and configuration
    ├── test_auth_handlers.py # Tests for auth_handlers.py
    ├── test_docs_handlers.py # Tests for docs_handlers.py
    └── test_handler.py       # Tests for handler.py
```

<!-- ## Contributing
Contributions are welcome! Please open issues and submit pull requests. -->