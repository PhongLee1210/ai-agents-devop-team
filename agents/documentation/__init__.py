"""
Documentation Agents

This module provides agents for tracking and documenting changes
made to the codebase by other agents.
"""

# Import the config and agent classes
from agents.documentation.documentation_agent import (
    DocumentationAgent,
    DocumentationConfig,
    ChangeRecord,
)

# Export all relevant classes
__all__ = [
    "DocumentationAgent",
    "DocumentationConfig",
    "ChangeRecord",
]
