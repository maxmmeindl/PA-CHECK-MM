"""
Tests for the Workflow Execution Engine.

This module contains tests for the workflow execution engine components.
"""
import unittest
from typing import Dict, Any

from ..rule_engine.rule_engine import RuleEngine, Rule, ListCondition
from .workflow_definition import WorkflowDefinition, State, StateType, Transition, WorkflowDefinitionError
from .workflow_instance import WorkflowInstance, WorkflowStatus, WorkflowInstanceError
from .workflow_engine import WorkflowEngine, WorkflowEngineError

class TestWorkflowDefinition(unittest.TestCase):
    """Tests for the WorkflowDefinition class."""
    
    def test_create_workflow_definition(self):
        """Test creating a workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="A test workflow"
        )
        self.assertEqual(workflow.id, "test_workflow")
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.description, "A test workflow")
    
    def test_add_state(self):
        """Test adding a state to a workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        state = State(
            id="test_state",
            name="Test State",
            description="A test state",
            type=StateType.NORMAL
        )
        
        workflow.add_state(state)
        self.assertIn("test_state", workflow.states)
        self.assertEqual(workflow.states["test_state"], state)
    
    def test_add_duplicate_state(self):
        """Test adding a duplicate state to a workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        state = State(
            id="test_state",
            name="Test State"
        )
        
        workflow.add_state(state)
        
        with self.assertRaises(WorkflowDefinitionError):
            workflow.add_state(state)
    
    def test_add_transition(self):
        """Test adding a transition to a workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        end_state = State(
            id="end",
            name="End",
            type=StateType.END
        )
        
        workflow.add_state(start_state)
        workflow.add_state(end_state)
        
        transition = Transition(
            id="start_to_end",
            name="Start to End",
            source_state_id="start",
            target_state_id="end"
        )
        
        workflow.add_transition(transition)
        self.assertIn("start_to_end", workflow.transitions)
        self.assertEqual(workflow.transitions["start_to_end"], transition)
    
    def test_add_transition_invalid_state(self):
        """Test adding a transition with an invalid state."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        workflow.add_state(start_state)
        
        transition = Transition(
            id="start_to_end",
            name="Start to End",
            source_state_id="start",
            target_state_id="end"  # This state doesn't exist
        )
        
        with self.assertRaises(WorkflowDefinitionError):
            workflow.add_transition(transition)
    
    def test_validate_workflow(self):
        """Test validating a workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        middle_state = State(
            id="middle",
            name="Middle"
        )
        
        end_state = State(
            id="end",
            name="End",
            type=StateType.END
        )
        
        workflow.add_state(start_state)
        workflow.add_state(middle_state)
        workflow.add_state(end_state)
        
        workflow.add_transition(Transition(
            id="start_to_middle",
            name="Start to Middle",
            source_state_id="start",
            target_state_id="middle"
        ))
        
        workflow.add_transition(Transition(
            id="middle_to_end",
            name="Middle to End",
            source_state_id="middle",
            target_state_id="end"
        ))
        
        # This should not raise an exception
        workflow.validate()
    
    def test_validate_workflow_no_start_state(self):
        """Test validating a workflow with no start state."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        state = State(
            id="test_state",
            name="Test State"
        )
        
        workflow.add_state(state)
        
        with self.assertRaises(WorkflowDefinitionError):
            workflow.validate()
    
    def test_validate_workflow_no_end_state(self):
        """Test validating a workflow with no end state."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        workflow.add_state(start_state)
        
        with self.assertRaises(WorkflowDefinitionError):
            workflow.validate()
    
    def test_validate_workflow_unreachable_end_state(self):
        """Test validating a workflow with an unreachable end state."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        end_state = State(
            id="end",
            name="End",
            type=StateType.END
        )
        
        workflow.add_state(start_state)
        workflow.add_state(end_state)
        
        # No transition from start to end
        
        with self.assertRaises(WorkflowDefinitionError):
            workflow.validate()
    
    def test_to_dict_and_from_dict(self):
        """Test converting a workflow definition to and from a dictionary."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="A test workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        end_state = State(
            id="end",
            name="End",
            type=StateType.END
        )
        
        workflow.add_state(start_state)
        workflow.add_state(end_state)
        
        workflow.add_transition(Transition(
            id="start_to_end",
            name="Start to End",
            source_state_id="start",
            target_state_id="end"
        ))
        
        # Convert to dictionary
        workflow_dict = workflow.to_dict()
        
        # Create a new workflow from the dictionary
        new_workflow = WorkflowDefinition.from_dict(workflow_dict)
        
        # Check that the new workflow is equivalent to the original
        self.assertEqual(new_workflow.id, workflow.id)
        self.assertEqual(new_workflow.name, workflow.name)
        self.assertEqual(new_workflow.description, workflow.description)
        self.assertEqual(len(new_workflow.states), len(workflow.states))
        self.assertEqual(len(new_workflow.transitions), len(workflow.transitions))
        self.assertEqual(new_workflow.start_state_id, workflow.start_state_id)
        self.assertEqual(new_workflow.end_state_ids, workflow.end_state_ids)

class TestWorkflowInstance(unittest.TestCase):
    """Tests for the WorkflowInstance class."""
    
    def setUp(self):
        """Set up a workflow definition for testing."""
        self.workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        middle_state = State(
            id="middle",
            name="Middle"
        )
        
        end_state = State(
            id="end",
            name="End",
            type=StateType.END
        )
        
        error_state = State(
            id="error",
            name="Error",
            type=StateType.ERROR
        )
        
        self.workflow.add_state(start_state)
        self.workflow.add_state(middle_state)
        self.workflow.add_state(end_state)
        self.workflow.add_state(error_state)
        
        self.workflow.add_transition(Transition(
            id="start_to_middle",
            name="Start to Middle",
            source_state_id="start",
            target_state_id="middle"
        ))
        
        self.workflow.add_transition(Transition(
            id="middle_to_end",
            name="Middle to End",
            source_state_id="middle",
            target_state_id="end"
        ))
        
        self.workflow.add_transition(Transition(
            id="middle_to_error",
            name="Middle to Error",
            source_state_id="middle",
            target_state_id="error"
        ))
    
    def test_create_workflow_instance(self):
        """Test creating a workflow instance."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow,
            context={"test": "value"}
        )
        
        self.assertEqual(instance.workflow_definition, self.workflow)
        self.assertEqual(instance.context, {"test": "value"})
        self.assertEqual(instance.current_state_id, "start")
        self.assertEqual(instance.status, WorkflowStatus.CREATED)
        self.assertEqual(len(instance.history), 1)
    
    def test_start_workflow_instance(self):
        """Test starting a workflow instance."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        
        self.assertEqual(instance.status, WorkflowStatus.RUNNING)
        self.assertEqual(len(instance.history), 2)
    
    def test_transition_to_state(self):
        """Test transitioning to a new state."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        try:
            instance.transition_to_state("middle", "start_to_middle")
            
            self.assertEqual(instance.current_state_id, "middle")
            self.assertEqual(instance.status, WorkflowStatus.RUNNING)
            self.assertEqual(len(instance.history), 3)
        except Exception as e:
            self.fail(f"Transition failed: {str(e)}")
    
    def test_transition_to_end_state(self):
        """Test transitioning to an end state."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        try:
            instance.transition_to_state("middle", "start_to_middle")
            instance.transition_to_state("end", "middle_to_end")
            
            self.assertEqual(instance.current_state_id, "end")
            self.assertEqual(instance.status, WorkflowStatus.COMPLETED)
            self.assertEqual(len(instance.history), 5)  # Created, Started, Transitioned, Transitioned, Completed
        except Exception as e:
            self.fail(f"Transition failed: {str(e)}")
    
    def test_transition_to_error_state(self):
        """Test transitioning to an error state."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        try:
            instance.transition_to_state("middle", "start_to_middle")
            instance.transition_to_state("error", "middle_to_error")
            
            self.assertEqual(instance.current_state_id, "error")
            self.assertEqual(instance.status, WorkflowStatus.FAILED)
            self.assertIsNotNone(instance.error)
            self.assertEqual(len(instance.history), 5)  # Created, Started, Transitioned, Transitioned, Failed
        except Exception as e:
            self.fail(f"Transition failed: {str(e)}")
    
    def test_fail_workflow_instance(self):
        """Test failing a workflow instance."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        instance.fail(Exception("Test error"))
        
        self.assertEqual(instance.status, WorkflowStatus.FAILED)
        self.assertIsNotNone(instance.error)
        self.assertEqual(len(instance.history), 3)  # Created, Started, Failed
    
    def test_suspend_and_resume_workflow_instance(self):
        """Test suspending and resuming a workflow instance."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        instance.suspend()
        
        self.assertEqual(instance.status, WorkflowStatus.SUSPENDED)
        
        instance.resume()
        
        self.assertEqual(instance.status, WorkflowStatus.RUNNING)
    
    def test_terminate_workflow_instance(self):
        """Test terminating a workflow instance."""
        instance = WorkflowInstance(
            workflow_definition=self.workflow
        )
        
        instance.start()
        instance.terminate()
        
        self.assertEqual(instance.status, WorkflowStatus.TERMINATED)

class TestWorkflowEngine(unittest.TestCase):
    """Tests for the WorkflowEngine class."""
    
    def setUp(self):
        """Set up a rule engine and workflow definition for testing."""
        # Create a rule engine
        self.rule_engine = RuleEngine()
        
        # Create a condition
        is_approved = ListCondition(
            field="approvals",
            operation="contains_all",
            value=["manager", "finance"]
        )
        
        # Create a rule
        approval_rule = Rule(
            id="approval_rule",
            name="Approval Rule",
            description="Check if the request has all required approvals",
            conditions=[is_approved],
            actions=[],
            priority=1
        )
        
        # Register the rule
        self.rule_engine.register_rule(approval_rule)
        
        # Create a workflow definition
        self.workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow"
        )
        
        start_state = State(
            id="start",
            name="Start",
            type=StateType.START
        )
        
        approval_state = State(
            id="approval",
            name="Approval"
        )
        
        approved_state = State(
            id="approved",
            name="Approved",
            type=StateType.END
        )
        
        rejected_state = State(
            id="rejected",
            name="Rejected",
            type=StateType.END
        )
        
        self.workflow.add_state(start_state)
        self.workflow.add_state(approval_state)
        self.workflow.add_state(approved_state)
        self.workflow.add_state(rejected_state)
        
        self.workflow.add_transition(Transition(
            id="start_to_approval",
            name="Start to Approval",
            source_state_id="start",
            target_state_id="approval"
        ))
        
        self.workflow.add_transition(Transition(
            id="approval_to_approved",
            name="Approval to Approved",
            source_state_id="approval",
            target_state_id="approved",
            condition_id="approval_rule"
        ))
        
        self.workflow.add_transition(Transition(
            id="approval_to_rejected",
            name="Approval to Rejected",
            source_state_id="approval",
            target_state_id="rejected"
        ))
        
        # Create a workflow engine
        self.workflow_engine = WorkflowEngine(self.rule_engine)
        
        # Register the workflow definition
        self.workflow_engine.register_workflow_definition(self.workflow)
    
    def test_create_workflow_instance(self):
        """Test creating a workflow instance."""
        instance = self.workflow_engine.create_workflow_instance(
            workflow_id="test_workflow",
            context={"test": "value"}
        )
        
        self.assertEqual(instance.workflow_definition, self.workflow)
        self.assertEqual(instance.context, {"test": "value"})
        self.assertEqual(instance.current_state_id, "start")
        self.assertEqual(instance.status, WorkflowStatus.CREATED)
    
    def test_run_workflow_instance(self):
        """Test running a workflow instance."""
        instance = self.workflow_engine.create_workflow_instance(
            workflow_id="test_workflow",
            context={"approvals": ["manager", "finance"]}
        )
        
        self.workflow_engine.run_workflow_instance(instance.instance_id)
        
        self.assertEqual(instance.current_state_id, "approved")
        self.assertEqual(instance.status, WorkflowStatus.COMPLETED)
    
    def test_run_workflow_instance_rejected(self):
        """Test running a workflow instance that gets rejected."""
        instance = self.workflow_engine.create_workflow_instance(
            workflow_id="test_workflow",
            context={"approvals": ["manager"]}  # Missing finance approval
        )
        
        self.workflow_engine.run_workflow_instance(instance.instance_id)
        
        self.assertEqual(instance.current_state_id, "rejected")
        self.assertEqual(instance.status, WorkflowStatus.COMPLETED)
    
    def test_create_and_run_workflow(self):
        """Test creating and running a workflow in a single operation."""
        instance = self.workflow_engine.create_and_run_workflow(
            workflow_id="test_workflow",
            context={"approvals": ["manager", "finance"]}
        )
        
        self.assertEqual(instance.current_state_id, "approved")
        self.assertEqual(instance.status, WorkflowStatus.COMPLETED)

if __name__ == "__main__":
    unittest.main()
