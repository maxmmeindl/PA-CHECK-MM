"""
Unit tests for the PA-CHECK-MM API.

This module contains unit tests for the API endpoints.
"""
import json
import uuid
from typing import Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.workflow.workflow_definition import WorkflowDefinition, StateType
from src.workflow.workflow_engine import WorkflowEngine
from src.workflow.workflow_instance import WorkflowInstance


# Create a global workflow engine for testing
global_workflow_engine = WorkflowEngine()


# Override the get_workflow_engine dependency
def get_test_workflow_engine():
    """Get the test workflow engine."""
    return global_workflow_engine


# Override the dependency in the app
from src.api.routers import get_workflow_engine
app.dependency_overrides[get_workflow_engine] = get_test_workflow_engine


# Test client
client = TestClient(app)


# Mock data
def create_test_workflow_definition() -> Dict:
    """Create a test workflow definition."""
    return {
        "id": f"test-workflow-{uuid.uuid4()}",
        "name": "Test Workflow",
        "description": "A test workflow",
        "states": [
            {
                "id": "start",
                "name": "Start",
                "description": "Start state",
                "type": "START",
                "metadata": {}
            },
            {
                "id": "processing",
                "name": "Processing",
                "description": "Processing state",
                "type": "NORMAL",
                "metadata": {}
            },
            {
                "id": "end",
                "name": "End",
                "description": "End state",
                "type": "END",
                "metadata": {}
            }
        ],
        "transitions": [
            {
                "id": "start-to-processing",
                "name": "Start to Processing",
                "description": "Transition from start to processing",
                "source_state_id": "start",
                "target_state_id": "processing",
                "priority": 0,
                "metadata": {}
            },
            {
                "id": "processing-to-end",
                "name": "Processing to End",
                "description": "Transition from processing to end",
                "source_state_id": "processing",
                "target_state_id": "end",
                "priority": 0,
                "metadata": {}
            }
        ],
        "start_state_id": "start"
    }


# Fixtures
@pytest.fixture
def workflow_definition() -> WorkflowDefinition:
    """Create a workflow definition for testing."""
    workflow_data = create_test_workflow_definition()
    
    # Create the workflow definition
    workflow = WorkflowDefinition(
        id=workflow_data["id"],
        name=workflow_data["name"],
        description=workflow_data["description"]
    )
    
    # Add states
    for state_data in workflow_data["states"]:
        state_type = getattr(StateType, state_data["type"])
        from src.workflow.workflow_definition import State
        state = State(
            id=state_data["id"],
            name=state_data["name"],
            description=state_data["description"],
            type=state_type,
            metadata=state_data["metadata"]
        )
        workflow.add_state(state)
    
    # Add transitions
    for transition_data in workflow_data["transitions"]:
        from src.workflow.workflow_definition import Transition
        transition = Transition(
            id=transition_data["id"],
            name=transition_data["name"],
            description=transition_data["description"],
            source_state_id=transition_data["source_state_id"],
            target_state_id=transition_data["target_state_id"],
            priority=transition_data["priority"],
            metadata=transition_data["metadata"]
        )
        workflow.add_transition(transition)
    
    # Register the workflow definition with the engine
    global_workflow_engine.register_workflow_definition(workflow)
    
    return workflow


@pytest.fixture
def workflow_instance(workflow_definition: WorkflowDefinition) -> WorkflowInstance:
    """Create a workflow instance for testing."""
    instance = global_workflow_engine.create_workflow_instance(workflow_definition.id)
    return instance


# Tests for workflow definitions
def test_list_workflows_empty():
    """Test listing workflows when there are none."""
    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert response.json() == []


def test_create_workflow():
    """Test creating a workflow definition."""
    workflow_data = create_test_workflow_definition()
    response = client.post("/api/workflows", json=workflow_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] == workflow_data["id"]
    assert data["name"] == workflow_data["name"]
    assert len(data["states"]) == 3
    assert len(data["transitions"]) == 2


def test_get_workflow():
    """Test getting a workflow definition."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Get the workflow
    workflow_id = workflow_data["id"]
    response = client.get(f"/api/workflows/{workflow_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == workflow_id
    assert data["name"] == workflow_data["name"]


def test_get_workflow_not_found():
    """Test getting a workflow definition that doesn't exist."""
    response = client.get("/api/workflows/non-existent-workflow")
    assert response.status_code == 404


def test_update_workflow():
    """Test updating a workflow definition."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Update the workflow
    workflow_id = workflow_data["id"]
    update_data = {
        "name": "Updated Workflow",
        "description": "An updated workflow"
    }
    response = client.put(f"/api/workflows/{workflow_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == workflow_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_workflow():
    """Test deleting a workflow definition."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Delete the workflow
    workflow_id = workflow_data["id"]
    response = client.delete(f"/api/workflows/{workflow_id}")
    assert response.status_code == 204
    
    # Verify the workflow is deleted
    get_response = client.get(f"/api/workflows/{workflow_id}")
    assert get_response.status_code == 404


# Tests for workflow instances
def test_list_instances_empty():
    """Test listing workflow instances when there are none."""
    response = client.get("/api/instances")
    assert response.status_code == 200
    assert response.json() == []


def test_start_instance():
    """Test starting a workflow instance."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Start an instance
    workflow_id = workflow_data["id"]
    instance_data = {
        "context": {"key": "value"}
    }
    response = client.post(f"/api/workflows/{workflow_id}/instances", json=instance_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["status"] == "RUNNING"
    assert data["context"] == instance_data["context"]


def test_get_instance():
    """Test getting a workflow instance."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Start an instance
    workflow_id = workflow_data["id"]
    instance_data = {"context": {}}
    start_response = client.post(f"/api/workflows/{workflow_id}/instances", json=instance_data)
    assert start_response.status_code == 201
    
    # Get the instance
    instance_id = start_response.json()["instance_id"]
    response = client.get(f"/api/instances/{instance_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["instance_id"] == instance_id
    assert data["workflow_id"] == workflow_id


def test_get_instance_not_found():
    """Test getting a workflow instance that doesn't exist."""
    response = client.get("/api/instances/non-existent-instance")
    assert response.status_code == 404


def test_transition_instance():
    """Test transitioning a workflow instance."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Start an instance
    workflow_id = workflow_data["id"]
    instance_data = {"context": {}}
    start_response = client.post(f"/api/workflows/{workflow_id}/instances", json=instance_data)
    assert start_response.status_code == 201
    
    # Transition the instance
    instance_id = start_response.json()["instance_id"]
    transition_data = {
        "target_state_id": "processing",
        "transition_id": "start-to-processing"
    }
    response = client.put(f"/api/instances/{instance_id}/transition", json=transition_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["instance_id"] == instance_id
    assert data["current_state_id"] == "processing"


def test_get_instance_history():
    """Test getting the history of a workflow instance."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    create_response = client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    
    # Start an instance
    workflow_id = workflow_data["id"]
    instance_data = {"context": {}}
    start_response = client.post(f"/api/workflows/{workflow_id}/instances", json=instance_data)
    assert start_response.status_code == 201
    
    # Get the instance history
    instance_id = start_response.json()["instance_id"]
    response = client.get(f"/api/instances/{instance_id}/history")
    assert response.status_code == 200
    
    data = response.json()
    assert data["instance_id"] == instance_id
    assert data["workflow_id"] == workflow_id
    assert isinstance(data["history"], list)
    assert len(data["history"]) > 0  # Should have at least one history entry


# Test health check
def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# Test root endpoint
def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()
    assert "version" in response.json()


# Test OpenAPI docs
def test_openapi_docs():
    """Test the OpenAPI docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json():
    """Test the OpenAPI JSON endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "/api/workflows" in data["paths"]
    assert "/api/instances" in data["paths"]
