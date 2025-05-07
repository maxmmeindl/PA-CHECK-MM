"""
Workflow Automation Package for PA-CHECK-MM Enterprise Solution.

This package provides a workflow execution engine that integrates with the business rules engine
to enable workflow automation.
"""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from .workflow_definition import (
    WorkflowDefinition,
    State,
    StateType,
    Transition,
    WorkflowError,
    WorkflowDefinitionError
)
from .workflow_instance import (
    WorkflowInstance,
    WorkflowStatus,
    HistoryEntry,
    WorkflowInstanceError
)
from .workflow_engine import (
    WorkflowEngine,
    WorkflowEngineError
)

__all__ = [
    'WorkflowDefinition',
    'State',
    'StateType',
    'Transition',
    'WorkflowError',
    'WorkflowDefinitionError',
    'WorkflowInstance',
    'WorkflowStatus',
    'HistoryEntry',
    'WorkflowInstanceError',
    'WorkflowEngine',
    'WorkflowEngineError'
]
