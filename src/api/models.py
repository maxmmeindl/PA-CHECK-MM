"""
Pydantic models for the PA-CHECK-MM API.

This module defines the request and response models for the API endpoints.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    status_code: int = 400
    error_type: Optional[str] = None


class StateTypeEnum(str, Enum):
    """Types of states in a workflow."""
    START = "START"
    NORMAL = "NORMAL"
    END = "END"
    ERROR = "ERROR"


class StateModel(BaseModel):
    """Model for a workflow state."""
    id: str
    name: str
    description: str = ""
    type: StateTypeEnum = StateTypeEnum.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransitionModel(BaseModel):
    """Model for a workflow transition."""
    id: str
    name: str
    source_state_id: str
    target_state_id: str
    condition_id: Optional[str] = None
    description: str = ""
    priority: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinitionBase(BaseModel):
    """Base model for workflow definition."""
    name: str
    description: str = ""


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """Model for creating a workflow definition."""
    id: str
    states: List[StateModel]
    transitions: List[TransitionModel]
    start_state_id: str


class WorkflowDefinitionUpdate(WorkflowDefinitionBase):
    """Model for updating a workflow definition."""
    states: Optional[List[StateModel]] = None
    transitions: Optional[List[TransitionModel]] = None
    start_state_id: Optional[str] = None


class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    """Response model for a workflow definition."""
    id: str
    states: List[StateModel]
    transitions: List[TransitionModel]
    start_state_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowStatusEnum(str, Enum):
    """Status of a workflow instance."""
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class HistoryEntryModel(BaseModel):
    """Model for a workflow history entry."""
    timestamp: datetime
    event_type: str
    details: str = ""
    state_id: Optional[str] = None
    transition_id: Optional[str] = None
    error: Optional[Dict[str, str]] = None


class WorkflowInstanceBase(BaseModel):
    """Base model for workflow instance."""
    context: Dict[str, Any] = Field(default_factory=dict)


class WorkflowInstanceCreate(WorkflowInstanceBase):
    """Model for creating a workflow instance."""
    instance_id: Optional[str] = None


class WorkflowInstanceTransition(BaseModel):
    """Model for transitioning a workflow instance."""
    target_state_id: str
    transition_id: Optional[str] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    """Response model for a workflow instance."""
    instance_id: str
    workflow_id: str
    current_state_id: str
    status: WorkflowStatusEnum
    error: Optional[Dict[str, str]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowInstanceHistoryResponse(BaseModel):
    """Response model for workflow instance history."""
    instance_id: str
    workflow_id: str
    history: List[HistoryEntryModel]
