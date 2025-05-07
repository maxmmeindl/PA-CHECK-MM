# PA-CHECK-MM API

This directory contains the RESTful API implementation for the PA-CHECK-MM Enterprise Solution workflow engine.

## Overview

The API provides endpoints for managing workflow definitions and instances, allowing users to:

- Create, read, update, and delete workflow definitions
- Start and manage workflow instances
- Transition workflow instances between states
- View workflow instance history

## API Endpoints

### Workflow Definitions

- `GET /api/workflows` - List all workflow definitions
- `GET /api/workflows/{workflow_id}` - Get a specific workflow definition
- `POST /api/workflows` - Create a new workflow definition
- `PUT /api/workflows/{workflow_id}` - Update a workflow definition
- `DELETE /api/workflows/{workflow_id}` - Delete a workflow definition

### Workflow Instances

- `GET /api/instances` - List all workflow instances
- `GET /api/instances/{instance_id}` - Get a specific workflow instance
- `POST /api/workflows/{workflow_id}/instances` - Start a new workflow instance
- `PUT /api/instances/{instance_id}/transition` - Transition a workflow instance to a new state
- `GET /api/instances/{instance_id}/history` - Get the history of a workflow instance

### Other Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /docs` - API documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI specification

## Implementation Details

The API is implemented using FastAPI and consists of the following components:

- `main.py` - Main FastAPI application
- `models.py` - Pydantic models for request and response validation
- `routers.py` - API route handlers

## Running the API

To run the API locally:

```bash
# Install dependencies
pip install fastapi uvicorn

# Run the API server
python -m src.api.main
```

The API will be available at http://localhost:8000.

## API Documentation

The API documentation is available at http://localhost:8000/docs when the server is running.

## Testing

Unit tests for the API are located in the `tests/api` directory. To run the tests:

```bash
pytest tests/api
```
