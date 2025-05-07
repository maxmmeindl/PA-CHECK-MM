# Workflow Execution Engine

This module provides a workflow execution engine for the PA-CHECK-MM enterprise solution. The workflow engine integrates with the business rules engine to enable workflow automation.

## Components

### WorkflowDefinition

The `WorkflowDefinition` class represents a workflow with states, transitions, conditions, and actions. It provides methods for:

- Adding states and transitions
- Validating the workflow structure
- Converting to/from JSON for persistence
- Analyzing workflow properties (e.g., reachable states)

### WorkflowInstance

The `WorkflowInstance` class represents a running instance of a workflow. It provides methods for:

- Tracking the current state and context data
- Transitioning between states
- Executing actions associated with states and transitions
- Maintaining an execution history
- Handling errors and status changes

### WorkflowEngine

The `WorkflowEngine` class is the main entry point for working with workflows. It provides methods for:

- Loading and managing workflow definitions
- Creating and running workflow instances
- Integrating with the business rules engine for evaluating conditions
- Handling errors and logging

## Usage

### Creating a Workflow Definition

```python
from workflow import WorkflowDefinition, State, StateType, Transition

# Create a workflow definition
workflow = WorkflowDefinition(
    id="purchase_request_workflow",
    name="Purchase Request Workflow",
    description="Workflow for processing purchase requests"
)

# Define states
submitted_state = State(
    id="submitted",
    name="Submitted",
    description="The purchase request has been submitted",
    type=StateType.START
)

review_state = State(
    id="review",
    name="Under Review",
    description="The purchase request is being reviewed"
)

completed_state = State(
    id="completed",
    name="Completed",
    description="The purchase request has been completed",
    type=StateType.END
)

# Add states to the workflow
workflow.add_state(submitted_state)
workflow.add_state(review_state)
workflow.add_state(completed_state)

# Define transitions
workflow.add_transition(Transition(
    id="submitted_to_review",
    name="Submit for Review",
    source_state_id="submitted",
    target_state_id="review"
))

workflow.add_transition(Transition(
    id="review_to_completed",
    name="Complete Request",
    source_state_id="review",
    target_state_id="completed",
    condition_id="approval_rule"  # Reference to a rule in the rule engine
))

# Validate the workflow
workflow.validate()
```

### Running a Workflow

```python
from workflow import WorkflowEngine
from rule_engine import RuleEngine

# Create a rule engine
rule_engine = RuleEngine()

# Register rules for workflow conditions
# ...

# Create a workflow engine
workflow_engine = WorkflowEngine(rule_engine)

# Register the workflow definition
workflow_engine.register_workflow_definition(workflow)

# Create a workflow instance
context = {
    "request_id": "PR-001",
    "requester": "John Doe",
    "amount": 1500.00,
    "tags": ["high_priority", "equipment"],
    "approvals": []
}
instance = workflow_engine.create_workflow_instance(
    workflow_id="purchase_request_workflow",
    context=context
)

# Run the workflow
workflow_engine.run_workflow_instance(instance.instance_id)

# Check the status
print(f"Status: {instance.status.name}")
print(f"Current State: {instance.current_state_id}")
```

### Loading Workflows from JSON

```python
# Load a workflow definition from a JSON file
workflow = workflow_engine.load_workflow_definition_from_file("workflows/purchase_request.json")

# Load all workflow definitions from a directory
workflows = workflow_engine.load_workflow_definitions_from_directory("workflows")
```

## Integration with Business Rules Engine

The workflow engine integrates with the business rules engine to evaluate conditions for transitions. When a workflow instance is running, the engine evaluates the conditions of outgoing transitions from the current state using the rule engine. If a condition evaluates to true, the corresponding transition is taken.

## Error Handling

The workflow engine includes comprehensive error handling:

- Validation errors when creating workflow definitions
- Runtime errors when executing workflow instances
- Integration errors when evaluating conditions

All errors are logged and can be handled by the application.

## Logging

The workflow engine uses Python's standard logging module to log events:

- Workflow definition registration and validation
- Workflow instance creation and execution
- State transitions and action execution
- Errors and exceptions

## Example

See the `example.py` file for a complete example of using the workflow engine.
