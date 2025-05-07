"""
Workflow Instance for PA-CHECK-MM Enterprise Solution.

This module provides the WorkflowInstance class that represents a running instance of a workflow.
"""
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .workflow_definition import WorkflowDefinition, State, StateType, WorkflowError

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowInstanceError(WorkflowError):
    """Exception raised when there is an error in a workflow instance."""
    pass

class WorkflowStatus(Enum):
    """Status of a workflow instance."""
    CREATED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SUSPENDED = auto()
    TERMINATED = auto()

@dataclass
class HistoryEntry:
    """
    Represents an entry in the workflow instance history.
    
    Attributes:
        timestamp: When the entry was created
        event_type: Type of event (e.g., 'STATE_ENTERED', 'TRANSITION_TAKEN')
        details: Additional details about the event
        state_id: ID of the state involved (if any)
        transition_id: ID of the transition involved (if any)
        error: Error information (if any)
    """
    timestamp: datetime
    event_type: str
    details: str = ""
    state_id: Optional[str] = None
    transition_id: Optional[str] = None
    error: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the history entry to a dictionary.
        
        Returns:
            A dictionary representation of the history entry
        """
        result = {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'details': self.details
        }
        
        if self.state_id:
            result['state_id'] = self.state_id
        if self.transition_id:
            result['transition_id'] = self.transition_id
        if self.error:
            result['error'] = {
                'type': type(self.error).__name__,
                'message': str(self.error)
            }
            
        return result

class WorkflowInstance:
    """
    Represents a running instance of a workflow.
    
    A workflow instance tracks the current state, context data, and execution history
    of a workflow. It provides methods for transitioning between states and handling errors.
    """
    
    def __init__(self, workflow_definition: WorkflowDefinition, context: Dict[str, Any] = None, instance_id: str = None):
        """
        Initialize a workflow instance.
        
        Args:
            workflow_definition: The workflow definition to use
            context: Initial context data for the workflow
            instance_id: Unique identifier for the instance (generated if not provided)
            
        Raises:
            WorkflowInstanceError: If the workflow definition is invalid
        """
        self.workflow_definition = workflow_definition
        self.context = context or {}
        self.instance_id = instance_id or str(uuid.uuid4())
        self.current_state_id = workflow_definition.start_state_id
        self.status = WorkflowStatus.CREATED
        self.history: List[HistoryEntry] = []
        self.error: Optional[Exception] = None
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.completed_at: Optional[datetime] = None
        self.logger = logging.getLogger(f"{__name__}.{self.instance_id}")
        
        # Validate the workflow definition
        if not workflow_definition.start_state_id:
            raise WorkflowInstanceError("Workflow definition has no start state")
        
        # Add initial history entry
        self._add_history_entry(
            event_type="INSTANCE_CREATED",
            details=f"Created workflow instance for workflow '{workflow_definition.id}'",
            state_id=self.current_state_id
        )
        
        self.logger.info(f"Created workflow instance '{self.instance_id}' for workflow '{workflow_definition.id}'")
    
    def start(self) -> None:
        """
        Start the workflow instance.
        
        Raises:
            WorkflowInstanceError: If the instance is not in CREATED status
        """
        if self.status != WorkflowStatus.CREATED:
            raise WorkflowInstanceError(f"Cannot start workflow instance in status '{self.status.name}'")
        
        self.status = WorkflowStatus.RUNNING
        self.updated_at = datetime.now()
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_STARTED",
            details="Started workflow instance",
            state_id=self.current_state_id
        )
        
        # Execute entry actions for the start state
        try:
            start_state = self.workflow_definition.get_state(self.current_state_id)
            self._execute_state_entry_actions(start_state)
        except Exception as e:
            self._handle_error(e, "Error executing entry actions for start state")
        
        self.logger.info(f"Started workflow instance '{self.instance_id}'")
    
    def complete(self) -> None:
        """
        Mark the workflow instance as completed.
        
        Raises:
            WorkflowInstanceError: If the instance is not in RUNNING status
                                  or if the current state is not an end state
        """
        if self.status != WorkflowStatus.RUNNING:
            raise WorkflowInstanceError(f"Cannot complete workflow instance in status '{self.status.name}'")
        
        if self.current_state_id not in self.workflow_definition.end_state_ids:
            raise WorkflowInstanceError(f"Cannot complete workflow instance: current state '{self.current_state_id}' is not an end state")
        
        self.status = WorkflowStatus.COMPLETED
        self.updated_at = datetime.now()
        self.completed_at = self.updated_at
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_COMPLETED",
            details="Completed workflow instance",
            state_id=self.current_state_id
        )
        
        self.logger.info(f"Completed workflow instance '{self.instance_id}'")
    
    def fail(self, error: Exception) -> None:
        """
        Mark the workflow instance as failed.
        
        Args:
            error: The error that caused the failure
        """
        self.status = WorkflowStatus.FAILED
        self.error = error
        self.updated_at = datetime.now()
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_FAILED",
            details=f"Failed workflow instance: {str(error)}",
            state_id=self.current_state_id,
            error=error
        )
        
        self.logger.error(f"Failed workflow instance '{self.instance_id}': {str(error)}")
    
    def suspend(self) -> None:
        """
        Suspend the workflow instance.
        
        Raises:
            WorkflowInstanceError: If the instance is not in RUNNING status
        """
        if self.status != WorkflowStatus.RUNNING:
            raise WorkflowInstanceError(f"Cannot suspend workflow instance in status '{self.status.name}'")
        
        self.status = WorkflowStatus.SUSPENDED
        self.updated_at = datetime.now()
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_SUSPENDED",
            details="Suspended workflow instance",
            state_id=self.current_state_id
        )
        
        self.logger.info(f"Suspended workflow instance '{self.instance_id}'")
    
    def resume(self) -> None:
        """
        Resume the workflow instance.
        
        Raises:
            WorkflowInstanceError: If the instance is not in SUSPENDED status
        """
        if self.status != WorkflowStatus.SUSPENDED:
            raise WorkflowInstanceError(f"Cannot resume workflow instance in status '{self.status.name}'")
        
        self.status = WorkflowStatus.RUNNING
        self.updated_at = datetime.now()
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_RESUMED",
            details="Resumed workflow instance",
            state_id=self.current_state_id
        )
        
        self.logger.info(f"Resumed workflow instance '{self.instance_id}'")
    
    def terminate(self) -> None:
        """
        Terminate the workflow instance.
        """
        self.status = WorkflowStatus.TERMINATED
        self.updated_at = datetime.now()
        
        # Add history entry
        self._add_history_entry(
            event_type="INSTANCE_TERMINATED",
            details="Terminated workflow instance",
            state_id=self.current_state_id
        )
        
        self.logger.info(f"Terminated workflow instance '{self.instance_id}'")
    
    def transition_to_state(self, state_id: str, transition_id: Optional[str] = None) -> None:
        """
        Transition to a new state.
        
        Args:
            state_id: The ID of the state to transition to
            transition_id: The ID of the transition to use (if any)
            
        Raises:
            WorkflowInstanceError: If the instance is not in RUNNING status
                                  or if the state does not exist
        """
        if self.status != WorkflowStatus.RUNNING:
            raise WorkflowInstanceError(f"Cannot transition workflow instance in status '{self.status.name}'")
        
        try:
            # Get the current and target states
            current_state = self.workflow_definition.get_state(self.current_state_id)
            target_state = self.workflow_definition.get_state(state_id)
            
            # Execute exit actions for the current state
            self._execute_state_exit_actions(current_state)
            
            # Execute transition actions if a transition ID is provided
            if transition_id:
                transition = self.workflow_definition.get_transition(transition_id)
                self._execute_transition_actions(transition)
            
            # Update the current state
            old_state_id = self.current_state_id
            self.current_state_id = state_id
            self.updated_at = datetime.now()
            
            # Add history entry
            self._add_history_entry(
                event_type="STATE_TRANSITIONED",
                details=f"Transitioned from state '{old_state_id}' to state '{state_id}'",
                state_id=state_id,
                transition_id=transition_id
            )
            
            # Execute entry actions for the target state
            self._execute_state_entry_actions(target_state)
            
            # Check if the target state is an end state
            if target_state.type == StateType.END:
                self.complete()
            # Check if the target state is an error state
            elif target_state.type == StateType.ERROR:
                self.fail(WorkflowInstanceError(f"Reached error state '{state_id}'"))
            
            self.logger.info(f"Transitioned workflow instance '{self.instance_id}' from state '{old_state_id}' to state '{state_id}'")
        except Exception as e:
            self._handle_error(e, f"Error transitioning to state '{state_id}'")
            raise
    
    def _execute_state_entry_actions(self, state: State) -> None:
        """
        Execute the entry actions for a state.
        
        Args:
            state: The state to execute entry actions for
            
        Raises:
            Exception: If an entry action fails
        """
        for action in state.entry_actions:
            try:
                action(self.context)
                self.logger.debug(f"Executed entry action for state '{state.id}'")
            except Exception as e:
                self.logger.error(f"Error executing entry action for state '{state.id}': {str(e)}")
                raise
    
    def _execute_state_exit_actions(self, state: State) -> None:
        """
        Execute the exit actions for a state.
        
        Args:
            state: The state to execute exit actions for
            
        Raises:
            Exception: If an exit action fails
        """
        for action in state.exit_actions:
            try:
                action(self.context)
                self.logger.debug(f"Executed exit action for state '{state.id}'")
            except Exception as e:
                self.logger.error(f"Error executing exit action for state '{state.id}': {str(e)}")
                raise
    
    def _execute_transition_actions(self, transition) -> None:
        """
        Execute the actions for a transition.
        
        Args:
            transition: The transition to execute actions for
            
        Raises:
            Exception: If a transition action fails
        """
        for action in transition.actions:
            try:
                action(self.context)
                self.logger.debug(f"Executed action for transition '{transition.id}'")
            except Exception as e:
                self.logger.error(f"Error executing action for transition '{transition.id}': {str(e)}")
                raise
    
    def _handle_error(self, error: Exception, message: str) -> None:
        """
        Handle an error in the workflow instance.
        
        Args:
            error: The error that occurred
            message: A message describing the error
        """
        self.logger.error(f"{message}: {str(error)}")
        
        # Add history entry
        self._add_history_entry(
            event_type="ERROR",
            details=message,
            state_id=self.current_state_id,
            error=error
        )
        
        # Fail the workflow instance
        self.fail(error)
    
    def _add_history_entry(self, event_type: str, details: str, state_id: Optional[str] = None, 
                          transition_id: Optional[str] = None, error: Optional[Exception] = None) -> None:
        """
        Add an entry to the workflow instance history.
        
        Args:
            event_type: Type of event
            details: Additional details about the event
            state_id: ID of the state involved (if any)
            transition_id: ID of the transition involved (if any)
            error: Error information (if any)
        """
        entry = HistoryEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            details=details,
            state_id=state_id,
            transition_id=transition_id,
            error=error
        )
        self.history.append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow instance to a dictionary.
        
        Returns:
            A dictionary representation of the workflow instance
        """
        return {
            'instance_id': self.instance_id,
            'workflow_id': self.workflow_definition.id,
            'current_state_id': self.current_state_id,
            'status': self.status.name,
            'context': self.context,
            'history': [entry.to_dict() for entry in self.history],
            'error': str(self.error) if self.error else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
