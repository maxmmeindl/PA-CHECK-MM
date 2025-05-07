"""
Debug script for API tests.
"""
import json
import uuid
from fastapi.testclient import TestClient

from src.api.main import app

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
    workflow_data = create_test_workflow_definition()
    print(f"Sending workflow data: {json.dumps(workflow_data, indent=2)}")
    
    response = client.post("/api/workflows", json=workflow_data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    main()
