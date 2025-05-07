"""
List Condition Implementation for PA-CHECK-MM Enterprise Solution.

This module provides a robust condition type for list operations.
"""
from typing import Any, Dict, List
from ..rule_engine import Condition, ConditionEvaluationError

class ListCondition(Condition):
    """
    Condition for list operations.
    
    Supports various list operations:
    - contains_all: All items in value must be in the field list
    - contains_any: At least one item in value must be in the field list
    - equals: The field list must contain the same items as value (order-independent)
    - is_subset: The field list must be a subset of value
    - is_superset: The field list must be a superset of value
    """
    
    VALID_OPERATIONS = ['contains_all', 'contains_any', 'equals', 'is_subset', 'is_superset']
    
    def __init__(self, field: str, operation: str, value: List[Any]):
        """
        Initialize a list condition.
        
        Args:
            field: The field path in the context to evaluate
            operation: The list operation to perform
            value: The list value to compare against
            
        Raises:
            ValueError: If the operation is not valid
        """
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(f"Invalid operation '{operation}'. Valid operations are: {', '.join(self.VALID_OPERATIONS)}")
        
        self.field = field
        self.operation = operation
        self.value = value
    
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
            
            # Handle edge cases
            if not isinstance(field_value, list):
                raise ConditionEvaluationError(f"Field '{self.field}' is not a list")
            
            # Empty list handling
            if not field_value and not self.value:
                # Both lists are empty
                if self.operation in ['equals', 'is_subset', 'is_superset']:
                    return True
                else:
                    return False
            elif not field_value:
                # Field list is empty
                if self.operation == 'is_subset':
                    return True
                else:
                    return False
            elif not self.value:
                # Value list is empty
                if self.operation == 'is_superset':
                    return True
                elif self.operation == 'contains_all':
                    return True
                else:
                    return False
            
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
                # This should never happen due to validation in __init__
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
