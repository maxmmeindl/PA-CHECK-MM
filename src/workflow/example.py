"""
Example usage of the Workflow Engine for PA-CHECK-MM Enterprise Solution.

This module demonstrates how to use the workflow engine to define and execute workflows.
"""
import logging
from typing import Dict, Any

from ..rule_engine.rule_engine import RuleEngine, Rule, ListCondition
from .workflow_definition import WorkflowDefinition, State, StateType, Transition
from .workflow_instance import WorkflowInstance, WorkflowStatus
from .workflow_engine import WorkflowEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_rule_engine() -> RuleEngine:
    """
    Create a sample rule engine with some rules.
    
    Returns:
        A rule engine with sample rules
    """
    rule_engine = RuleEngine()
    
    # Create some conditions
    is_high_priority = ListCondition(
        field="tags",
        operation="contains_any",
        value=["high_priority", "urgent"]
    )
    
    is_low_priority = ListCondition(
        field="tags",
        operation="contains_any",
        value=["low_priority", "routine"]
    )
    
    is_approved = ListCondition(
        field="approvals",
        operation="contains_all",
        value=["manager", "finance"]
    )
    
    # Create some rules
    high_priority_rule = Rule(
        id="high_priority_rule",
        name="High Priority Rule",
        description="Check if the request is high priority",
        conditions=[is_high_priority],
        actions=[],
        priority=10
    )
    
    low_priority_rule = Rule(
        id="low_priority_rule",
        name="Low Priority Rule",
        description="Check if the request is low priority",
        conditions=[is_low_priority],
        actions=[],
        priority=5
    )
    
    approval_rule = Rule(
        id="approval_rule",
        name="Approval Rule",
        description="Check if the request has all required approvals",
        conditions=[is_approved],
        actions=[],
        priority=8
    )
    
    # Register the rules
    rule_engine.register_rule(high_priority_rule)
    rule_engine.register_rule(low_priority_rule)
    rule_engine.register_rule(approval_rule)
    
    return rule_engine

def create_sample_workflow_definition() -> WorkflowDefinition:
    """
    Create a sample workflow definition for a purchase request.
    
    Returns:
        A workflow definition
    """
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
    
    approval_state = State(
        id="approval",
        name="Awaiting Approval",
        description="The purchase request is awaiting approval"
    )
    
    processing_state = State(
        id="processing",
        name="Processing",
        description="The purchase request is being processed"
    )
    
    completed_state = State(
        id="completed",
        name="Completed",
        description="The purchase request has been completed",
        type=StateType.END
    )
    
    rejected_state = State(
        id="rejected",
        name="Rejected",
        description="The purchase request has been rejected",
        type=StateType.END
    )
    
    error_state = State(
        id="error",
        name="Error",
        description="An error occurred while processing the purchase request",
        type=StateType.ERROR
    )
    
    # Add states to the workflow
    workflow.add_state(submitted_state)
    workflow.add_state(review_state)
    workflow.add_state(approval_state)
    workflow.add_state(processing_state)
    workflow.add_state(completed_state)
    workflow.add_state(rejected_state)
    workflow.add_state(error_state)
    
    # Define transitions
    # From Submitted to Review
    workflow.add_transition(Transition(
        id="submitted_to_review",
        name="Submit for Review",
        source_state_id="submitted",
        target_state_id="review"
    ))
    
    # From Review to Approval (high priority)
    workflow.add_transition(Transition(
        id="review_to_approval_high",
        name="Send for Approval (High Priority)",
        source_state_id="review",
        target_state_id="approval",
        condition_id="high_priority_rule",
        priority=10
    ))
    
    # From Review to Approval (low priority)
    workflow.add_transition(Transition(
        id="review_to_approval_low",
        name="Send for Approval (Low Priority)",
        source_state_id="review",
        target_state_id="approval",
        condition_id="low_priority_rule",
        priority=5
    ))
    
    # From Review to Rejected
    workflow.add_transition(Transition(
        id="review_to_rejected",
        name="Reject Request",
        source_state_id="review",
        target_state_id="rejected"
    ))
    
    # From Approval to Processing
    workflow.add_transition(Transition(
        id="approval_to_processing",
        name="Process Approved Request",
        source_state_id="approval",
        target_state_id="processing",
        condition_id="approval_rule"
    ))
    
    # From Approval to Rejected
    workflow.add_transition(Transition(
        id="approval_to_rejected",
        name="Reject Request",
        source_state_id="approval",
        target_state_id="rejected"
    ))
    
    # From Processing to Completed
    workflow.add_transition(Transition(
        id="processing_to_completed",
        name="Complete Request",
        source_state_id="processing",
        target_state_id="completed"
    ))
    
    # From Processing to Error
    workflow.add_transition(Transition(
        id="processing_to_error",
        name="Error Processing Request",
        source_state_id="processing",
        target_state_id="error"
    ))
    
    return workflow

def log_workflow_status(instance: WorkflowInstance) -> None:
    """
    Log the status of a workflow instance.
    
    Args:
        instance: The workflow instance to log
    """
    logger.info(f"Workflow Instance: {instance.instance_id}")
    logger.info(f"Status: {instance.status.name}")
    logger.info(f"Current State: {instance.current_state_id}")
    logger.info(f"Context: {instance.context}")
    logger.info(f"History: {len(instance.history)} events")
    for i, entry in enumerate(instance.history):
        logger.info(f"  {i+1}. {entry.event_type}: {entry.details}")

def run_example() -> None:
    """
    Run an example workflow.
    """
    # Create a rule engine
    rule_engine = create_sample_rule_engine()
    
    # Create a workflow engine
    workflow_engine = WorkflowEngine(rule_engine)
    
    # Create a workflow definition
    workflow_definition = create_sample_workflow_definition()
    
    # Register the workflow definition
    workflow_engine.register_workflow_definition(workflow_definition)
    
    # Create a workflow instance with high priority
    high_priority_context = {
        "request_id": "PR-001",
        "requester": "John Doe",
        "amount": 1500.00,
        "tags": ["high_priority", "equipment"],
        "approvals": []
    }
    high_priority_instance = workflow_engine.create_workflow_instance(
        workflow_id="purchase_request_workflow",
        context=high_priority_context
    )
    
    # Run the high priority workflow
    logger.info("Running high priority workflow...")
    workflow_engine.run_workflow_instance(high_priority_instance.instance_id)
    log_workflow_status(high_priority_instance)
    
    # Add approvals and continue
    logger.info("Adding approvals and continuing...")
    high_priority_instance.context["approvals"] = ["manager", "finance"]
    workflow_engine.run_workflow_instance(high_priority_instance.instance_id)
    log_workflow_status(high_priority_instance)
    
    # Create a workflow instance with low priority
    low_priority_context = {
        "request_id": "PR-002",
        "requester": "Jane Smith",
        "amount": 500.00,
        "tags": ["low_priority", "office_supplies"],
        "approvals": []
    }
    low_priority_instance = workflow_engine.create_workflow_instance(
        workflow_id="purchase_request_workflow",
        context=low_priority_context
    )
    
    # Run the low priority workflow
    logger.info("Running low priority workflow...")
    workflow_engine.run_workflow_instance(low_priority_instance.instance_id)
    log_workflow_status(low_priority_instance)
    
    # Create a workflow instance that will be rejected
    reject_context = {
        "request_id": "PR-003",
        "requester": "Bob Johnson",
        "amount": 5000.00,
        "tags": ["high_priority", "travel"],
        "approvals": ["manager"]  # Missing finance approval
    }
    reject_instance = workflow_engine.create_and_run_workflow(
        workflow_id="purchase_request_workflow",
        context=reject_context
    )
    log_workflow_status(reject_instance)

if __name__ == "__main__":
    run_example()
