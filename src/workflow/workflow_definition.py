"""
Workflow Definition for PA-CHECK-MM Enterprise Solution.

This module provides the WorkflowDefinition class that represents a workflow with states,
transitions, conditions, and actions.
"""
import json
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Union

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowError(Exception):
    """Base exception for all workflow errors."""
    pass

class WorkflowDefinitionError(WorkflowError):
    """Exception raised when there is an error in a workflow definition."""
    pass

class StateType(Enum):
    """Types of states in a workflow."""
    START = auto()
    NORMAL = auto()
    END = auto()
    ERROR = auto()

@dataclass
class State:
    """
    Represents a state in a workflow.
    
    Attributes:
        id: Unique identifier for the state
        name: Human-readable name for the state
        description: Detailed description of the state
        type: Type of the state (START, NORMAL, END, ERROR)
        metadata: Additional metadata for the state
        entry_actions: Actions to execute when entering the state
        exit_actions: Actions to execute when exiting the state
    """
    id: str
    name: str
    description: str = ""
    type: StateType = StateType.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_actions: List[Callable[[Dict[str, Any]], None]] = field(default_factory=list)
    exit_actions: List[Callable[[Dict[str, Any]], None]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the state after initialization."""
        if not self.id:
            raise WorkflowDefinitionError("State ID cannot be empty")
        if not self.name:
            raise WorkflowDefinitionError("State name cannot be empty")

@dataclass
class Transition:
    """
    Represents a transition between states in a workflow.
    
    Attributes:
        id: Unique identifier for the transition
        name: Human-readable name for the transition
        description: Detailed description of the transition
        source_state_id: ID of the source state
        target_state_id: ID of the target state
        condition_id: ID of the condition to evaluate for this transition
        priority: Priority of the transition (higher priority transitions are evaluated first)
        actions: Actions to execute when the transition is taken
        metadata: Additional metadata for the transition
    """
    id: str
    name: str
    source_state_id: str
    target_state_id: str
    condition_id: Optional[str] = None
    description: str = ""
    priority: int = 0
    actions: List[Callable[[Dict[str, Any]], None]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the transition after initialization."""
        if not self.id:
            raise WorkflowDefinitionError("Transition ID cannot be empty")
        if not self.name:
            raise WorkflowDefinitionError("Transition name cannot be empty")
        if not self.source_state_id:
            raise WorkflowDefinitionError("Source state ID cannot be empty")
        if not self.target_state_id:
            raise WorkflowDefinitionError("Target state ID cannot be empty")

class WorkflowDefinition:
    """
    Represents a workflow with states, transitions, conditions, and actions.
    
    A workflow consists of states connected by transitions. Transitions are triggered
    by conditions and can execute actions. The workflow progresses from a start state
    to an end state based on the evaluation of conditions.
    """
    
    def __init__(self, id: str, name: str, description: str = ""):
        """
        Initialize a workflow definition.
        
        Args:
            id: Unique identifier for the workflow
            name: Human-readable name for the workflow
            description: Detailed description of the workflow
            
        Raises:
            WorkflowDefinitionError: If the ID or name is empty
        """
        if not id:
            raise WorkflowDefinitionError("Workflow ID cannot be empty")
        if not name:
            raise WorkflowDefinitionError("Workflow name cannot be empty")
            
        self.id = id
        self.name = name
        self.description = description
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, Transition] = {}
        self.metadata: Dict[str, Any] = {}
        self.logger = logger
        
        # Track start and end states
        self.start_state_id: Optional[str] = None
        self.end_state_ids: Set[str] = set()
        self.error_state_ids: Set[str] = set()
    
    def add_state(self, state: State) -> None:
        """
        Add a state to the workflow.
        
        Args:
            state: The state to add
            
        Raises:
            WorkflowDefinitionError: If a state with the same ID already exists
        """
        if state.id in self.states:
            raise WorkflowDefinitionError(f"State with ID '{state.id}' already exists")
            
        self.states[state.id] = state
        
        # Track special states
        if state.type == StateType.START:
            if self.start_state_id is not None:
                raise WorkflowDefinitionError("Workflow already has a start state")
            self.start_state_id = state.id
        elif state.type == StateType.END:
            self.end_state_ids.add(state.id)
        elif state.type == StateType.ERROR:
            self.error_state_ids.add(state.id)
            
        self.logger.info(f"Added state '{state.id}' to workflow '{self.id}'")
    
    def add_transition(self, transition: Transition) -> None:
        """
        Add a transition to the workflow.
        
        Args:
            transition: The transition to add
            
        Raises:
            WorkflowDefinitionError: If a transition with the same ID already exists
                                    or if the source or target state does not exist
        """
        if transition.id in self.transitions:
            raise WorkflowDefinitionError(f"Transition with ID '{transition.id}' already exists")
            
        # Validate source and target states
        if transition.source_state_id not in self.states:
            raise WorkflowDefinitionError(f"Source state '{transition.source_state_id}' does not exist")
        if transition.target_state_id not in self.states:
            raise WorkflowDefinitionError(f"Target state '{transition.target_state_id}' does not exist")
            
        self.transitions[transition.id] = transition
        self.logger.info(f"Added transition '{transition.id}' to workflow '{self.id}'")
    
    def get_state(self, state_id: str) -> State:
        """
        Get a state by ID.
        
        Args:
            state_id: The ID of the state to get
            
        Returns:
            The state
            
        Raises:
            KeyError: If the state is not found
        """
        if state_id in self.states:
            return self.states[state_id]
        else:
            raise KeyError(f"State '{state_id}' not found")
    
    def get_transition(self, transition_id: str) -> Transition:
        """
        Get a transition by ID.
        
        Args:
            transition_id: The ID of the transition to get
            
        Returns:
            The transition
            
        Raises:
            KeyError: If the transition is not found
        """
        if transition_id in self.transitions:
            return self.transitions[transition_id]
        else:
            raise KeyError(f"Transition '{transition_id}' not found")
    
    def get_outgoing_transitions(self, state_id: str) -> List[Transition]:
        """
        Get all transitions that originate from a state.
        
        Args:
            state_id: The ID of the state
            
        Returns:
            A list of transitions
            
        Raises:
            KeyError: If the state is not found
        """
        if state_id not in self.states:
            raise KeyError(f"State '{state_id}' not found")
            
        # Find all transitions with the given source state ID
        # Sort by priority (higher priority first)
        return sorted(
            [t for t in self.transitions.values() if t.source_state_id == state_id],
            key=lambda t: -t.priority
        )
    
    def validate(self) -> None:
        """
        Validate the workflow definition.
        
        Raises:
            WorkflowDefinitionError: If the workflow is invalid
        """
        # Check if there is a start state
        if self.start_state_id is None:
            raise WorkflowDefinitionError("Workflow must have a start state")
            
        # Check if there is at least one end state
        if not self.end_state_ids:
            raise WorkflowDefinitionError("Workflow must have at least one end state")
            
        # Check if all states are reachable from the start state
        reachable_states = self._get_reachable_states(self.start_state_id)
        unreachable_states = set(self.states.keys()) - reachable_states
        if unreachable_states:
            self.logger.warning(f"Unreachable states in workflow '{self.id}': {', '.join(unreachable_states)}")
            
        # Check if at least one end state is reachable
        if not any(state_id in reachable_states for state_id in self.end_state_ids):
            raise WorkflowDefinitionError("No end state is reachable from the start state")
            
        self.logger.info(f"Validated workflow '{self.id}'")
    
    def _get_reachable_states(self, start_state_id: str) -> Set[str]:
        """
        Get all states that are reachable from a given state.
        
        Args:
            start_state_id: The ID of the state to start from
            
        Returns:
            A set of state IDs that are reachable
        """
        reachable_states = {start_state_id}
        queue = [start_state_id]
        
        while queue:
            current_state_id = queue.pop(0)
            outgoing_transitions = self.get_outgoing_transitions(current_state_id)
            
            for transition in outgoing_transitions:
                target_state_id = transition.target_state_id
                if target_state_id not in reachable_states:
                    reachable_states.add(target_state_id)
                    queue.append(target_state_id)
        
        return reachable_states
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow definition to a dictionary.
        
        Returns:
            A dictionary representation of the workflow
        """
        # Convert states to dictionaries
        states_dict = {}
        for state_id, state in self.states.items():
            states_dict[state_id] = {
                'id': state.id,
                'name': state.name,
                'description': state.description,
                'type': state.type.name,
                'metadata': state.metadata
                # Note: entry_actions and exit_actions are not serialized
            }
        
        # Convert transitions to dictionaries
        transitions_dict = {}
        for transition_id, transition in self.transitions.items():
            transitions_dict[transition_id] = {
                'id': transition.id,
                'name': transition.name,
                'description': transition.description,
                'source_state_id': transition.source_state_id,
                'target_state_id': transition.target_state_id,
                'condition_id': transition.condition_id,
                'priority': transition.priority,
                'metadata': transition.metadata
                # Note: actions are not serialized
            }
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata,
            'states': states_dict,
            'transitions': transitions_dict,
            'start_state_id': self.start_state_id,
            'end_state_ids': list(self.end_state_ids),
            'error_state_ids': list(self.error_state_ids)
        }
    
    def to_json(self) -> str:
        """
        Convert the workflow definition to a JSON string.
        
        Returns:
            A JSON string representation of the workflow
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition':
        """
        Create a workflow definition from a dictionary.
        
        Args:
            data: The dictionary representation of the workflow
            
        Returns:
            A workflow definition
            
        Raises:
            WorkflowDefinitionError: If the dictionary is invalid
        """
        try:
            # Create the workflow
            workflow = cls(
                id=data['id'],
                name=data['name'],
                description=data.get('description', '')
            )
            
            # Set metadata
            workflow.metadata = data.get('metadata', {})
            
            # Add states
            for state_data in data.get('states', {}).values():
                state_type = StateType[state_data.get('type', 'NORMAL')]
                state = State(
                    id=state_data['id'],
                    name=state_data['name'],
                    description=state_data.get('description', ''),
                    type=state_type,
                    metadata=state_data.get('metadata', {})
                )
                workflow.add_state(state)
            
            # Add transitions
            for transition_data in data.get('transitions', {}).values():
                transition = Transition(
                    id=transition_data['id'],
                    name=transition_data['name'],
                    description=transition_data.get('description', ''),
                    source_state_id=transition_data['source_state_id'],
                    target_state_id=transition_data['target_state_id'],
                    condition_id=transition_data.get('condition_id'),
                    priority=transition_data.get('priority', 0),
                    metadata=transition_data.get('metadata', {})
                )
                workflow.add_transition(transition)
            
            # Validate the workflow
            workflow.validate()
            
            return workflow
        except KeyError as e:
            raise WorkflowDefinitionError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise WorkflowDefinitionError(f"Error creating workflow from dictionary: {str(e)}")
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorkflowDefinition':
        """
        Create a workflow definition from a JSON string.
        
        Args:
            json_str: The JSON string representation of the workflow
            
        Returns:
            A workflow definition
            
        Raises:
            WorkflowDefinitionError: If the JSON string is invalid
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise WorkflowDefinitionError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            raise WorkflowDefinitionError(f"Error creating workflow from JSON: {str(e)}")
