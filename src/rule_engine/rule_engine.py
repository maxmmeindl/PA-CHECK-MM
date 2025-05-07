"""
Rule Engine for PA-CHECK-MM Enterprise Solution.

This module provides the core functionality for defining and executing business rules.
"""
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)

class RuleEngineError(Exception):
    """Base exception for all rule engine errors."""
    pass

class ConditionEvaluationError(RuleEngineError):
    """Exception raised when a condition cannot be evaluated."""
    pass

class ActionExecutionError(RuleEngineError):
    """Exception raised when an action cannot be executed."""
    pass

@dataclass
class Condition:
    """Base class for all conditions."""
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition against the provided context.
        
        Args:
            context: The context data to evaluate against
            
        Returns:
            bool: True if the condition is met, False otherwise
            
        Raises:
            ConditionEvaluationError: If the condition cannot be evaluated
        """
        raise NotImplementedError("Subclasses must implement evaluate()")

@dataclass
class ListCondition(Condition):
    """Condition for list operations."""
    field: str
    operation: str  # 'contains_all', 'contains_any', 'equals', 'is_subset', 'is_superset'
    value: List[Any]
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the list condition against the provided context.
        
        Args:
            context: The context data to evaluate against
            
        Returns:
            bool: True if the condition is met, False otherwise
            
        Raises:
            ConditionEvaluationError: If the condition cannot be evaluated
        """
        try:
            # Get the field value from the context
            field_value = self._get_field_value(context, self.field)
            
            # Ensure field_value is a list
            if not isinstance(field_value, list):
                raise ConditionEvaluationError(f"Field '{self.field}' is not a list")
                
            # Evaluate based on the operation
            if self.operation == 'contains_all':
                return all(item in field_value for item in self.value)
            elif self.operation == 'contains_any':
                return any(item in field_value for item in self.value)
            elif self.operation == 'equals':
                return set(field_value) == set(self.value)
            elif self.operation == 'is_subset':
                return set(field_value).issubset(set(self.value))
            elif self.operation == 'is_superset':
                return set(field_value).issuperset(set(self.value))
            else:
                raise ConditionEvaluationError(f"Unknown operation '{self.operation}'")
        except KeyError:
            raise ConditionEvaluationError(f"Field '{self.field}' not found in context")
        except Exception as e:
            raise ConditionEvaluationError(f"Error evaluating list condition: {str(e)}")
    
    def _get_field_value(self, context: Dict[str, Any], field_path: str) -> Any:
        """
        Get a field value from the context using a dot-notation path.
        
        Args:
            context: The context data
            field_path: The path to the field, e.g., 'user.address.city'
            
        Returns:
            The field value
            
        Raises:
            KeyError: If the field is not found
        """
        parts = field_path.split('.')
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value[part]
            else:
                raise KeyError(f"Cannot access '{part}' in '{field_path}'")
        return value

@dataclass
class Rule:
    """A business rule with conditions and actions."""
    id: str
    name: str
    description: str
    conditions: List[Condition]
    actions: List[Callable[[Dict[str, Any]], None]]
    priority: int = 0
    enabled: bool = True
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate all conditions of the rule against the provided context.
        
        Args:
            context: The context data to evaluate against
            
        Returns:
            bool: True if all conditions are met, False otherwise
            
        Raises:
            ConditionEvaluationError: If a condition cannot be evaluated
        """
        if not self.enabled:
            return False
            
        try:
            return all(condition.evaluate(context) for condition in self.conditions)
        except Exception as e:
            logger.error(f"Error evaluating rule '{self.id}': {str(e)}")
            raise ConditionEvaluationError(f"Error evaluating rule '{self.id}': {str(e)}")
    
    def execute(self, context: Dict[str, Any]) -> None:
        """
        Execute all actions of the rule with the provided context.
        
        Args:
            context: The context data to use for action execution
            
        Raises:
            ActionExecutionError: If an action cannot be executed
        """
        try:
            for action in self.actions:
                action(context)
        except Exception as e:
            logger.error(f"Error executing rule '{self.id}': {str(e)}")
            raise ActionExecutionError(f"Error executing rule '{self.id}': {str(e)}")

class RuleEngine:
    """Engine for managing and executing business rules."""
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.logger = logger
    
    def register_rule(self, rule: Rule) -> None:
        """
        Register a rule with the engine.
        
        Args:
            rule: The rule to register
        """
        self.rules[rule.id] = rule
        self.logger.info(f"Registered rule '{rule.id}'")
    
    def unregister_rule(self, rule_id: str) -> None:
        """
        Unregister a rule from the engine.
        
        Args:
            rule_id: The ID of the rule to unregister
            
        Raises:
            KeyError: If the rule is not found
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Unregistered rule '{rule_id}'")
        else:
            raise KeyError(f"Rule '{rule_id}' not found")
    
    def get_rule(self, rule_id: str) -> Rule:
        """
        Get a rule by ID.
        
        Args:
            rule_id: The ID of the rule to get
            
        Returns:
            The rule
            
        Raises:
            KeyError: If the rule is not found
        """
        if rule_id in self.rules:
            return self.rules[rule_id]
        else:
            raise KeyError(f"Rule '{rule_id}' not found")
    
    def get_all_rules(self) -> List[Rule]:
        """
        Get all registered rules.
        
        Returns:
            A list of all rules
        """
        return list(self.rules.values())
    
    def evaluate_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a rule by ID against the provided context.
        
        Args:
            rule_id: The ID of the rule to evaluate
            context: The context data to evaluate against
            
        Returns:
            bool: True if the rule conditions are met, False otherwise
            
        Raises:
            KeyError: If the rule is not found
            ConditionEvaluationError: If a condition cannot be evaluated
        """
        rule = self.get_rule(rule_id)
        return rule.evaluate(context)
    
    def execute_rule(self, rule_id: str, context: Dict[str, Any]) -> None:
        """
        Execute a rule by ID with the provided context.
        
        Args:
            rule_id: The ID of the rule to execute
            context: The context data to use for action execution
            
        Raises:
            KeyError: If the rule is not found
            ActionExecutionError: If an action cannot be executed
        """
        rule = self.get_rule(rule_id)
        rule.execute(context)
    
    def evaluate_and_execute(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a rule and execute it if the conditions are met.
        
        Args:
            rule_id: The ID of the rule to evaluate and execute
            context: The context data to use
            
        Returns:
            bool: True if the rule was executed, False otherwise
            
        Raises:
            KeyError: If the rule is not found
            ConditionEvaluationError: If a condition cannot be evaluated
            ActionExecutionError: If an action cannot be executed
        """
        rule = self.get_rule(rule_id)
        if rule.evaluate(context):
            rule.execute(context)
            return True
        return False
    
    def evaluate_all(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """
        Evaluate all rules against the provided context.
        
        Args:
            context: The context data to evaluate against
            
        Returns:
            A dictionary mapping rule IDs to evaluation results
        """
        results = {}
        for rule_id, rule in self.rules.items():
            try:
                results[rule_id] = rule.evaluate(context)
            except Exception as e:
                self.logger.error(f"Error evaluating rule '{rule_id}': {str(e)}")
                results[rule_id] = False
        return results
    
    def execute_matching(self, context: Dict[str, Any]) -> List[str]:
        """
        Execute all rules whose conditions are met by the provided context.
        
        Args:
            context: The context data to use
            
        Returns:
            A list of IDs of rules that were executed
        """
        executed_rules = []
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.rules.values(), key=lambda r: -r.priority)
        
        for rule in sorted_rules:
            try:
                if rule.evaluate(context):
                    rule.execute(context)
                    executed_rules.append(rule.id)
            except Exception as e:
                self.logger.error(f"Error executing rule '{rule.id}': {str(e)}")
        
        return executed_rules
