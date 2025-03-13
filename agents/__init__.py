"""
DevGenius AI Agents Module

This module provides a collection of AI agents for automating DevOps workflows
for frontend applications. The agents are organized into categories:

- analysis: Agents for analyzing the codebase and predicting build status
- infrastructure: Agents for creating infrastructure (Docker, etc.)
- ci_cd: Agents for handling CI/CD pipelines
- documentation: Agents for tracking and documenting changes
"""

# Import all agents from their respective modules
from agents.analysis import TechStackAgent, BuildPredictorAgent
from agents.infrastructure import DockerfileAgent, BuildStatusAgent
from agents.ci_cd import GitHubActionsAgent, CodeReviewAgent
from agents.documentation import DocumentationAgent

# Export all agents
__all__ = [
    # Analysis agents
    "TechStackAgent",
    "BuildPredictorAgent",
    # Infrastructure agents
    "DockerfileAgent",
    "BuildStatusAgent",
    # CI/CD agents
    "GitHubActionsAgent",
    "CodeReviewAgent",
    # Documentation agents
    "DocumentationAgent",
    # Chat agent
    "ChatAgent",
]
