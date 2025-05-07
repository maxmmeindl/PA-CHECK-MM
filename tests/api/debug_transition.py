"""
Debug script for transition API test.
"""
import json
import uuid
from fastapi.testclient import TestClient

from src.api.main import app
from src.workflow.workflow_engine import WorkflowEngine
from src.workflow.workflow_definition import WorkflowDefinition, StateType, State, Transition

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


def create_test_workflow_definition():
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


def main():
    """Main function."""
    # Create a workflow
    workflow_data = create_test_workflow_definition()
    print(f"Creating workflow: {workflow_data['id']}")
    create_response = client.post("/api/workflows", json=workflow_data)
    print(f"Create workflow status: {create_response.status_code}")
    
    # Start an instance
    workflow_id = workflow_data["id"]
    instance_data = {"context": {}}
    print(f"Starting instance for workflow: {workflow_id}")
    start_response = client.post(f"/api/workflows/{workflow_id}/instances", json=instance_data)
    print(f"Start instance status: {start_response.status_code}")
    
    if start_response.status_code == 201:
        instance_id = start_response.json()["instance_id"]
        print(f"Instance ID: {instance_id}")
        
        # Get the instance
        get_response = client.get(f"/api/instances/{instance_id}")
        print(f"Get instance status: {get_response.status_code}")
        print(f"Instance: {json.dumps(get_response.json(), indent=2)}")
        
        # Transition the instance
        transition_data = {
            "target_state_id": "processing",
            "transition_id": "start-to-processing"
        }
        print(f"Transitioning instance: {instance_id}")
        response = client.put(f"/api/instances/{instance_id}/transition", json=transition_data)
        print(f"Transition status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    main()
