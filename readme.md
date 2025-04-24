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
| PUT    | /tasks/{taskId}/status    | Update task status (authenticated)   |
| DELETE | /tasks/{taskId}           | Delete a task (authenticated)        |

All `/tasks` routes require an `Authorization: Bearer <token>` header.

## Testing

- `test_db_connection.py` verifies access to MongoDB.
- Add more unit/integration tests as needed.

## Documentation
- Raw OpenAPI spec: [`docs/openapi.yaml`](docs/openapi.yaml)
- Static HTML docs: [`docs/index.html`](docs/index.html) (open directly in your browser)
- Interactive docs: run `python open_docs.py` to serve and open docs at http://localhost:8000

## Project Structure
```
auth_handlers.py   # Registration & login logic
db.py              # MongoDB client setup
handler.py         # Task CRUD handlers
serverless.yml     # Serverless service configuration
requirements.txt   # Python dependencies
package.json       # Dev dependencies (Serverless plugins)
docs/              # API documentation (OpenAPI + HTML)
tests/             # (future) additional test files
```  

## Contributing
Contributions are welcome! Please open issues and submit pull requests.

