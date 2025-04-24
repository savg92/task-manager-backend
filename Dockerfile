# Use an official Python runtime as a parent image
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by some Python packages
# (Example: build-essential for C extensions, libpq-dev for psycopg2)
# Add any specific dependencies your project needs
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# Install Poetry (if using - adjust if using pip directly)
# RUN pip install poetry

# Copy only the dependency definition files first to leverage Docker cache
COPY requirements.txt ./
# COPY pyproject.toml poetry.lock* ./

# Install dependencies
# Using --no-cache-dir reduces image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# --- Final Stage ---
# Use a slim base image for the final stage
FROM python:3.12-slim

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# The Serverless framework will package this code. No CMD or ENTRYPOINT needed for Lambda deployment.
# If you were running a traditional web server (Flask/Django), you would add:
# EXPOSE 8000
# CMD ["python", "your_server_script.py"]
