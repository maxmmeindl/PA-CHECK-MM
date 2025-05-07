"""
Workflow Engine for PA-CHECK-MM Enterprise Solution.

This module provides the WorkflowEngine class that can load workflow definitions,
create instances, and execute workflows.
"""
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..rule_engine.rule_engine import RuleEngine, ConditionEvaluationError
from .workflow_definition import WorkflowDefinition, State, StateType, Transition, WorkflowDefinitionError
from .workflow_instance import WorkflowInstance, WorkflowStatus, WorkflowInstanceError

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowEngineError(Exception):
    """Base exception for all workflow engine errors."""
    pass

class WorkflowEngine:
    """
    Engine for managing and executing workflows.
    
    The workflow engine is responsible for:
    - Loading and managing workflow definitions
    - Creating and managing workflow instances
    - Executing workflow instances
    - Integrating with the rule engine for evaluating conditions
    """
    
    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        """
        Initialize a workflow engine.
        
        Args:
            rule_engine: The rule engine to use for evaluating conditions
        """
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.workflow_instances: Dict[str, WorkflowInstance] = {}
        self.rule_engine = rule_engine or RuleEngine()
        self.logger = logger
    
    def register_workflow_definition(self, workflow_definition: WorkflowDefinition) -> None:
        """
        Register a workflow definition with the engine.
        
        Args:
            workflow_definition: The workflow definition to register
            
        Raises:
            WorkflowEngineError: If a workflow definition with the same ID already exists
        """
        if workflow_definition.id in self.workflow_definitions:
            raise WorkflowEngineError(f"Workflow definition with ID '{workflow_definition.id}' already exists")
            
        # Validate the workflow definition
        try:
            workflow_definition.validate()
        except WorkflowDefinitionError as e:
            raise WorkflowEngineError(f"Invalid workflow definition: {str(e)}")
            
        self.workflow_definitions[workflow_definition.id] = workflow_definition
        self.logger.info(f"Registered workflow definition '{workflow_definition.id}'")
    
    def unregister_workflow_definition(self, workflow_id: str) -> None:
        """
        Unregister a workflow definition from the engine.
        
        Args:
            workflow_id: The ID of the workflow definition to unregister
            
        Raises:
            KeyError: If the workflow definition is not found
        """
        if workflow_id in self.workflow_definitions:
            del self.workflow_definitions[workflow_id]
            self.logger.info(f"Unregistered workflow definition '{workflow_id}'")
        else:
            raise KeyError(f"Workflow definition '{workflow_id}' not found")
    
    def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition:
        """
        Get a workflow definition by ID.
        
        Args:
            workflow_id: The ID of the workflow definition to get
            
        Returns:
            The workflow definition
            
        Raises:
            KeyError: If the workflow definition is not found
        """
        if workflow_id in self.workflow_definitions:
            return self.workflow_definitions[workflow_id]
        else:
            raise KeyError(f"Workflow definition '{workflow_id}' not found")
    
    def get_all_workflow_definitions(self) -> List[WorkflowDefinition]:
        """
        Get all registered workflow definitions.
        
        Returns:
            A list of all workflow definitions
        """
        return list(self.workflow_definitions.values())
    
    def load_workflow_definition_from_dict(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """
        Load a workflow definition from a dictionary.
        
        Args:
            data: The dictionary representation of the workflow definition
            
        Returns:
            The loaded workflow definition
            
        Raises:
            WorkflowEngineError: If the dictionary is invalid
        """
        try:
            workflow_definition = WorkflowDefinition.from_dict(data)
            self.register_workflow_definition(workflow_definition)
            return workflow_definition
        except Exception as e:
            raise WorkflowEngineError(f"Error loading workflow definition from dictionary: {str(e)}")
    
    def load_workflow_definition_from_json(self, json_str: str) -> WorkflowDefinition:
        """
        Load a workflow definition from a JSON string.
        
        Args:
            json_str: The JSON string representation of the workflow definition
            
        Returns:
            The loaded workflow definition
            
        Raises:
            WorkflowEngineError: If the JSON string is invalid
        """
        try:
            workflow_definition = WorkflowDefinition.from_json(json_str)
            self.register_workflow_definition(workflow_definition)
            return workflow_definition
        except Exception as e:
            raise WorkflowEngineError(f"Error loading workflow definition from JSON: {str(e)}")
    
    def load_workflow_definition_from_file(self, file_path: str) -> WorkflowDefinition:
        """
        Load a workflow definition from a JSON file.
        
        Args:
            file_path: The path to the JSON file
            
        Returns:
            The loaded workflow definition
            
        Raises:
            WorkflowEngineError: If the file cannot be read or is invalid
        """
        try:
            with open(file_path, 'r') as f:
                json_str = f.read()
            return self.load_workflow_definition_from_json(json_str)
        except Exception as e:
            raise WorkflowEngineError(f"Error loading workflow definition from file '{file_path}': {str(e)}")
    
    def load_workflow_definitions_from_directory(self, directory_path: str) -> List[WorkflowDefinition]:
        """
        Load all workflow definitions from JSON files in a directory.
        
        Args:
            directory_path: The path to the directory
            
        Returns:
            A list of loaded workflow definitions
            
        Raises:
            WorkflowEngineError: If the directory cannot be read
        """
        try:
            workflow_definitions = []
            for filename in os.listdir(directory_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(directory_path, filename)
                    try:
                        workflow_definition = self.load_workflow_definition_from_file(file_path)
                        workflow_definitions.append(workflow_definition)
                    except WorkflowEngineError as e:
                        self.logger.error(f"Error loading workflow definition from file '{file_path}': {str(e)}")
            return workflow_definitions
        except Exception as e:
            raise WorkflowEngineError(f"Error loading workflow definitions from directory '{directory_path}': {str(e)}")
    
    def create_workflow_instance(self, workflow_id: str, context: Dict[str, Any] = None, instance_id: str = None) -> WorkflowInstance:
        """
        Create a new workflow instance.
        
        Args:
            workflow_id: The ID of the workflow definition to use
            context: Initial context data for the workflow
            instance_id: Unique identifier for the instance (generated if not provided)
            
        Returns:
            The created workflow instance
            
        Raises:
            KeyError: If the workflow definition is not found
            WorkflowEngineError: If the workflow instance cannot be created
        """
        try:
            workflow_definition = self.get_workflow_definition(workflow_id)
            instance = WorkflowInstance(workflow_definition, context, instance_id)
            self.workflow_instances[instance.instance_id] = instance
            self.logger.info(f"Created workflow instance '{instance.instance_id}' for workflow '{workflow_id}'")
            return instance
        except KeyError:
            raise KeyError(f"Workflow definition '{workflow_id}' not found")
        except Exception as e:
            raise WorkflowEngineError(f"Error creating workflow instance: {str(e)}")
    
    def get_workflow_instance(self, instance_id: str) -> WorkflowInstance:
        """
        Get a workflow instance by ID.
        
        Args:
            instance_id: The ID of the workflow instance to get
            
        Returns:
            The workflow instance
            
        Raises:
            KeyError: If the workflow instance is not found
        """
        if instance_id in self.workflow_instances:
            return self.workflow_instances[instance_id]
        else:
            raise KeyError(f"Workflow instance '{instance_id}' not found")
    
    def get_all_workflow_instances(self) -> List[WorkflowInstance]:
        """
        Get all workflow instances.
        
        Returns:
            A list of all workflow instances
        """
        return list(self.workflow_instances.values())
    
    def start_workflow_instance(self, instance_id: str) -> None:
        """
        Start a workflow instance.
        
        Args:
            instance_id: The ID of the workflow instance to start
            
        Raises:
            KeyError: If the workflow instance is not found
            WorkflowInstanceError: If the instance is not in CREATED status
        """
        instance = self.get_workflow_instance(instance_id)
        instance.start()
        self.logger.info(f"Started workflow instance '{instance_id}'")
    
    def run_workflow_instance(self, instance_id: str, max_transitions: int = 100) -> WorkflowInstance:
        """
        Run a workflow instance until it completes, fails, or reaches the maximum number of transitions.
        
        Args:
            instance_id: The ID of the workflow instance to run
            max_transitions: Maximum number of transitions to execute
            
        Returns:
            The workflow instance
            
        Raises:
            KeyError: If the workflow instance is not found
            WorkflowEngineError: If the workflow instance cannot be run
        """
        instance = self.get_workflow_instance(instance_id)
        
        # Start the instance if it's not already running
        if instance.status == WorkflowStatus.CREATED:
            instance.start()
        
        # Run the instance until it completes, fails, or reaches the maximum number of transitions
        transitions_executed = 0
        try:
            while (instance.status == WorkflowStatus.RUNNING and 
                   transitions_executed < max_transitions):
                # Get the current state
                current_state_id = instance.current_state_id
                
                # Get outgoing transitions from the current state
                outgoing_transitions = instance.workflow_definition.get_outgoing_transitions(current_state_id)
                
                # Find the first transition whose condition evaluates to true
                transition_taken = False
                for transition in outgoing_transitions:
                    if self._evaluate_transition_condition(transition, instance.context):
                        # Take the transition
                        instance.transition_to_state(transition.target_state_id, transition.id)
                        transitions_executed += 1
                        transition_taken = True
                        break
                
                # If no transition was taken, we're stuck
                if not transition_taken:
                    self.logger.warning(f"Workflow instance '{instance_id}' is stuck in state '{current_state_id}': no valid transition")
                    break
            
            # Check if we reached the maximum number of transitions
            if transitions_executed >= max_transitions:
                instance.fail(WorkflowEngineError(f"Exceeded maximum number of transitions ({max_transitions})"))
            
            return instance
        except Exception as e:
            self.logger.error(f"Error running workflow instance '{instance_id}': {str(e)}")
            instance.fail(e)
            raise WorkflowEngineError(f"Error running workflow instance '{instance_id}': {str(e)}")
    
    def create_and_run_workflow(self, workflow_id: str, context: Dict[str, Any] = None, 
                               max_transitions: int = 100) -> WorkflowInstance:
        """
        Create and run a workflow instance in a single operation.
        
        Args:
            workflow_id: The ID of the workflow definition to use
            context: Initial context data for the workflow
            max_transitions: Maximum number of transitions to execute
            
        Returns:
            The workflow instance
            
        Raises:
            KeyError: If the workflow definition is not found
            WorkflowEngineError: If the workflow instance cannot be created or run
        """
        instance = self.create_workflow_instance(workflow_id, context)
        return self.run_workflow_instance(instance.instance_id, max_transitions)
    
    def _evaluate_transition_condition(self, transition: Transition, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition for a transition.
        
        Args:
            transition: The transition to evaluate
            context: The context data to evaluate against
            
        Returns:
            True if the condition is met or if there is no condition, False otherwise
        """
        # If there is no condition, the transition is always valid
        if not transition.condition_id:
            return True
        
        try:
            # Evaluate the condition using the rule engine
            return self.rule_engine.evaluate_rule(transition.condition_id, context)
        except KeyError:
            self.logger.error(f"Condition '{transition.condition_id}' not found in rule engine")
            return False
        except ConditionEvaluationError as e:
            self.logger.error(f"Error evaluating condition '{transition.condition_id}': {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error evaluating condition '{transition.condition_id}': {str(e)}")
            return False
