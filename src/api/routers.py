"""
API routers for the PA-CHECK-MM workflow engine.

This module defines the API endpoints for the workflow engine.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from ..workflow.workflow_definition import WorkflowDefinition, WorkflowDefinitionError, StateType, State, Transition
from ..workflow.workflow_engine import WorkflowEngine, WorkflowEngineError
from ..workflow.workflow_instance import WorkflowInstance, WorkflowInstanceError, WorkflowStatus
from .models import (
    ErrorResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
    WorkflowInstanceCreate,
    WorkflowInstanceHistoryResponse,
    WorkflowInstanceResponse,
    WorkflowInstanceTransition,
)


# Create router
router = APIRouter(prefix="/api", tags=["workflow"])


# Dependency to get the workflow engine
def get_workflow_engine() -> WorkflowEngine:
    """Get the workflow engine singleton."""
    # In a real application, this would be a singleton or retrieved from a dependency injection container
    return WorkflowEngine()


# Error handling
def handle_workflow_error(e: Exception) -> ErrorResponse:
    """Convert a workflow error to an API error response."""
    if isinstance(e, KeyError):
        return ErrorResponse(
            detail=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="NotFound"
        )
    elif isinstance(e, (WorkflowDefinitionError, WorkflowInstanceError)):
        return ErrorResponse(
            detail=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type=e.__class__.__name__
        )
    elif isinstance(e, WorkflowEngineError):
        return ErrorResponse(
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=e.__class__.__name__
        )
    else:
        return ErrorResponse(
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=e.__class__.__name__
        )


# Helper functions
def workflow_definition_to_response(workflow: WorkflowDefinition) -> WorkflowDefinitionResponse:
    """Convert a workflow definition to a response model."""
    # Handle states based on the actual structure of the WorkflowDefinition class
    states = []
    for state_id, state in workflow.states.items():
        states.append({
            "id": state.id,
            "name": state.name,
            "description": state.description,
            "type": state.type.name,
            "metadata": state.metadata
        })
    
    # Handle transitions based on the actual structure of the WorkflowDefinition class
    transitions = []
    for transition_id, transition in workflow.transitions.items():
        transitions.append({
            "id": transition.id,
            "name": transition.name,
            "description": transition.description,
            "source_state_id": transition.source_state_id,
            "target_state_id": transition.target_state_id,
            "condition_id": transition.condition_id,
            "priority": transition.priority,
            "metadata": transition.metadata
        })
    
    return WorkflowDefinitionResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        states=states,
        transitions=transitions,
        start_state_id=workflow.start_state_id,
        created_at=getattr(workflow, "created_at", None),
        updated_at=getattr(workflow, "updated_at", None)
    )


def workflow_instance_to_response(instance: WorkflowInstance) -> WorkflowInstanceResponse:
    """Convert a workflow instance to a response model."""
    error_dict = None
    if instance.error:
        error_dict = {
            "type": type(instance.error).__name__,
            "message": str(instance.error)
        }
    
    return WorkflowInstanceResponse(
        instance_id=instance.instance_id,
        workflow_id=instance.workflow_definition.id,
        current_state_id=instance.current_state_id,
        status=instance.status.name,
        context=instance.context,
        error=error_dict,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        completed_at=instance.completed_at
    )


def workflow_instance_history_to_response(instance: WorkflowInstance) -> WorkflowInstanceHistoryResponse:
    """Convert a workflow instance history to a response model."""
    history_entries = [entry.to_dict() for entry in instance.history]
    
    return WorkflowInstanceHistoryResponse(
        instance_id=instance.instance_id,
        workflow_id=instance.workflow_definition.id,
        history=history_entries
    )


# Workflow Definition Endpoints
@router.get(
    "/workflows",
    response_model=List[WorkflowDefinitionResponse],
    summary="List all workflow definitions",
    description="Returns a list of all registered workflow definitions."
)
async def list_workflows(
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> List[WorkflowDefinitionResponse]:
    """List all workflow definitions."""
    try:
        workflows = engine.get_all_workflow_definitions()
        return [workflow_definition_to_response(workflow) for workflow in workflows]
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowDefinitionResponse,
    summary="Get a specific workflow definition",
    description="Returns a specific workflow definition by ID."
)
async def get_workflow(
    workflow_id: str = Path(..., description="The ID of the workflow definition"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowDefinitionResponse:
    """Get a specific workflow definition."""
    try:
        workflow = engine.get_workflow_definition(workflow_id)
        return workflow_definition_to_response(workflow)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.post(
    "/workflows",
    response_model=WorkflowDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow definition",
    description="Creates a new workflow definition."
)
async def create_workflow(
    workflow_data: WorkflowDefinitionCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowDefinitionResponse:
    """Create a new workflow definition."""
    try:
        # Create the workflow definition
        workflow = WorkflowDefinition(
            id=workflow_data.id,
            name=workflow_data.name,
            description=workflow_data.description
        )
        
        # Add states
        for state_data in workflow_data.states:
            state_type = getattr(StateType, state_data.type.value)
            state = State(
                id=state_data.id,
                name=state_data.name,
                description=state_data.description,
                type=state_type,
                metadata=state_data.metadata
            )
            workflow.add_state(state)
        
        # Add transitions
        for transition_data in workflow_data.transitions:
            transition = Transition(
                id=transition_data.id,
                name=transition_data.name,
                description=transition_data.description,
                source_state_id=transition_data.source_state_id,
                target_state_id=transition_data.target_state_id,
                condition_id=transition_data.condition_id,
                priority=transition_data.priority,
                metadata=transition_data.metadata
            )
            workflow.add_transition(transition)
        
        # Validate the workflow definition
        workflow.validate()
        
        # Register the workflow definition with the engine
        engine.register_workflow_definition(workflow)
        
        return workflow_definition_to_response(workflow)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.put(
    "/workflows/{workflow_id}",
    response_model=WorkflowDefinitionResponse,
    summary="Update a workflow definition",
    description="Updates an existing workflow definition."
)
async def update_workflow(
    workflow_data: WorkflowDefinitionUpdate,
    workflow_id: str = Path(..., description="The ID of the workflow definition"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowDefinitionResponse:
    """Update a workflow definition."""
    try:
        # Get the existing workflow definition
        workflow = engine.get_workflow_definition(workflow_id)
        
        # Update the workflow definition
        if workflow_data.name is not None:
            workflow.name = workflow_data.name
        if workflow_data.description is not None:
            workflow.description = workflow_data.description
        if workflow_data.start_state_id is not None:
            workflow.start_state_id = workflow_data.start_state_id
        
        # Update states if provided
        if workflow_data.states is not None:
            # Clear existing states
            workflow.states.clear()
            
            # Add new states
            for state_data in workflow_data.states:
                state_dict = state_data.dict()
                workflow.add_state_from_dict(state_dict)
        
        # Update transitions if provided
        if workflow_data.transitions is not None:
            # Clear existing transitions
            workflow.transitions.clear()
            
            # Add new transitions
            for transition_data in workflow_data.transitions:
                transition_dict = transition_data.dict()
                workflow.add_transition_from_dict(transition_dict)
        
        # Validate the updated workflow definition
        workflow.validate()
        
        # Update the workflow definition in the engine
        engine.workflow_definitions[workflow_id] = workflow
        
        return workflow_definition_to_response(workflow)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.delete(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow definition",
    description="Deletes a workflow definition."
)
async def delete_workflow(
    workflow_id: str = Path(..., description="The ID of the workflow definition"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> None:
    """Delete a workflow definition."""
    try:
        engine.unregister_workflow_definition(workflow_id)
        return None
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


# Workflow Instance Endpoints
@router.get(
    "/instances",
    response_model=List[WorkflowInstanceResponse],
    summary="List all workflow instances",
    description="Returns a list of all workflow instances."
)
async def list_instances(
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> List[WorkflowInstanceResponse]:
    """List all workflow instances."""
    try:
        instances = engine.get_all_workflow_instances()
        return [workflow_instance_to_response(instance) for instance in instances]
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.get(
    "/instances/{instance_id}",
    response_model=WorkflowInstanceResponse,
    summary="Get a specific workflow instance",
    description="Returns a specific workflow instance by ID."
)
async def get_instance(
    instance_id: str = Path(..., description="The ID of the workflow instance"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowInstanceResponse:
    """Get a specific workflow instance."""
    try:
        instance = engine.get_workflow_instance(instance_id)
        return workflow_instance_to_response(instance)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.post(
    "/workflows/{workflow_id}/instances",
    response_model=WorkflowInstanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new workflow instance",
    description="Creates and starts a new workflow instance."
)
async def start_instance(
    instance_data: WorkflowInstanceCreate,
    workflow_id: str = Path(..., description="The ID of the workflow definition"),
    auto_run: bool = Query(False, description="Whether to automatically run the workflow instance"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowInstanceResponse:
    """Start a new workflow instance."""
    try:
        # Create the workflow instance
        instance = engine.create_workflow_instance(
            workflow_id=workflow_id,
            context=instance_data.context,
            instance_id=instance_data.instance_id
        )
        
        # Start the workflow instance
        if auto_run:
            instance = engine.run_workflow_instance(instance.instance_id)
        else:
            engine.start_workflow_instance(instance.instance_id)
        
        return workflow_instance_to_response(instance)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.put(
    "/instances/{instance_id}/transition",
    response_model=WorkflowInstanceResponse,
    summary="Transition a workflow instance",
    description="Transitions a workflow instance to a new state."
)
async def transition_instance(
    transition_data: WorkflowInstanceTransition,
    instance_id: str = Path(..., description="The ID of the workflow instance"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowInstanceResponse:
    """Transition a workflow instance to a new state."""
    try:
        # Get the workflow instance
        instance = engine.get_workflow_instance(instance_id)
        
        # Check if the instance is in a valid state for transitioning
        if instance.status != WorkflowStatus.RUNNING:
            raise WorkflowInstanceError(f"Cannot transition instance with status '{instance.status.name}'")
        
        # Transition the instance to the new state
        instance.transition_to_state(
            state_id=transition_data.target_state_id,
            transition_id=transition_data.transition_id
        )
        
        return workflow_instance_to_response(instance)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )


@router.get(
    "/instances/{instance_id}/history",
    response_model=WorkflowInstanceHistoryResponse,
    summary="Get the history of a workflow instance",
    description="Returns the history of a workflow instance."
)
async def get_instance_history(
    instance_id: str = Path(..., description="The ID of the workflow instance"),
    engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowInstanceHistoryResponse:
    """Get the history of a workflow instance."""
    try:
        instance = engine.get_workflow_instance(instance_id)
        return workflow_instance_history_to_response(instance)
    except Exception as e:
        error = handle_workflow_error(e)
        raise HTTPException(
            status_code=error.status_code,
            detail=error.dict()
        )
