"""
Priority Handler for PA-CHECK-MM Enterprise Solution.

This module manages rule priorities and execution order.
"""
import logging
from typing import Dict, List, Optional, Tuple
from ..rule_engine import Rule

# Configure logging
logger = logging.getLogger(__name__)

class PriorityConflictError(Exception):
    """Exception raised when there is a conflict in rule priorities."""
    pass

class PriorityHandler:
    """
    Manages rule priorities and execution order.
    
    Features:
    - Stable sorting algorithm to maintain relative order for rules with equal priorities
    - Conflict detection for rules with the same priority
    - Logging for priority conflicts
    - Graceful fallback behavior in case of errors
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize a priority handler.
        
        Args:
            strict_mode: If True, raise an exception on priority conflicts
        """
        self.strict_mode = strict_mode
        self.logger = logger
    
    def sort_rules(self, rules: List[Rule]) -> List[Rule]:
        """
        Sort rules by priority (higher priority first) in a stable manner.
        
        Args:
            rules: The rules to sort
            
        Returns:
            The sorted rules
            
        Raises:
            PriorityConflictError: If strict_mode is True and there are priority conflicts
        """
        # Check for priority conflicts
        conflicts = self._detect_conflicts(rules)
        if conflicts:
            conflict_msg = self._format_conflicts(conflicts)
            self.logger.warning(f"Priority conflicts detected: {conflict_msg}")
            if self.strict_mode:
                raise PriorityConflictError(conflict_msg)
        
        # Sort rules by priority (higher priority first)
        # Using negative priority for descending order
        # Using the rule's position in the original list as a secondary key for stability
        return sorted(enumerate(rules), key=lambda x: (-x[1].priority, x[0]))
    
    def _detect_conflicts(self, rules: List[Rule]) -> Dict[int, List[str]]:
        """
        Detect priority conflicts among rules.
        
        Args:
            rules: The rules to check
            
        Returns:
            A dictionary mapping priorities to lists of rule IDs with that priority
        """
        priority_map: Dict[int, List[str]] = {}
        conflicts: Dict[int, List[str]] = {}
        
        for rule in rules:
            priority = rule.priority
            if priority not in priority_map:
                priority_map[priority] = []
            priority_map[priority].append(rule.id)
            
            # If there are multiple rules with the same priority, it's a conflict
            if len(priority_map[priority]) > 1:
                conflicts[priority] = priority_map[priority]
        
        return conflicts
    
    def _format_conflicts(self, conflicts: Dict[int, List[str]]) -> str:
        """
        Format priority conflicts for logging.
        
        Args:
            conflicts: A dictionary mapping priorities to lists of rule IDs with that priority
            
        Returns:
            A formatted string describing the conflicts
        """
        conflict_strs = []
        for priority, rule_ids in conflicts.items():
            conflict_strs.append(f"Priority {priority}: {', '.join(rule_ids)}")
        return "; ".join(conflict_strs)
    
    def get_rule_priority(self, rule: Rule, default: int = 0) -> int:
        """
        Get the priority of a rule with a safe default.
        
        Args:
            rule: The rule to get the priority of
            default: The default priority to use if the rule has no priority
            
        Returns:
            The rule's priority
        """
        try:
            return rule.priority
        except (AttributeError, TypeError):
            self.logger.warning(f"Rule '{rule.id}' has no priority, using default {default}")
            return default
