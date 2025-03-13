from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from utils.groq_client import GROQClient
from typing import Dict, List, Any, Optional
import os
import json
import datetime
import difflib
from dataclasses import dataclass, field


class DocumentationConfig(BaseModel):
    """
    Configuration settings for the Documentation agent.

    Attributes:
        groq_api_endpoint (str): GROQ API endpoint URL
        groq_api_key (str): Authentication key for GROQ API
        output_dir (str): Directory to save documentation
        model (str): GROQ model to use
    """

    groq_api_endpoint: str
    groq_api_key: str
    output_dir: str = "docs"
    model: str = "llama3-8b-8192"


@dataclass
class ChangeRecord:
    """Record of a change made by an agent"""

    agent_name: str
    timestamp: str
    file_path: str
    change_description: str
    diff: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class DocumentationAgent(Agent):
    """
    An AI agent that tracks changes made by other agents and documents them.

    This agent monitors actions taken by other AI agents, records file changes,
    and generates comprehensive documentation of all modifications.
    """

    def __init__(self, config: DocumentationConfig):
        """
        Initialize the Documentation agent with necessary configuration.

        Args:
            config (DocumentationConfig): Configuration for the documentation agent
        """
        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )
        self.changes: List[ChangeRecord] = []
        self.file_snapshots: Dict[str, str] = {}

        # Create output directory if it doesn't exist
        os.makedirs(config.output_dir, exist_ok=True)

    def record_file_snapshot(self, file_path: str) -> None:
        """
        Record the current state of a file before changes are made.

        Args:
            file_path (str): Path to the file to snapshot
        """
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
                self.file_snapshots[file_path] = content

    def record_change(
        self,
        agent_name: str,
        file_path: str,
        change_description: str,
        details: Dict[str, Any] = None,
    ) -> None:
        """
        Record a change made by an agent.

        Args:
            agent_name (str): Name of the agent making the change
            file_path (str): Path to the file that was changed
            change_description (str): Description of the change
            details (Dict[str, Any], optional): Additional details about the change
        """
        timestamp = datetime.datetime.now().isoformat()
        diff = None

        # Calculate diff if we have a snapshot
        if file_path in self.file_snapshots and os.path.exists(file_path):
            with open(file_path, "r") as f:
                new_content = f.read()
                old_content = self.file_snapshots[file_path]

                diff_lines = difflib.unified_diff(
                    old_content.splitlines(),
                    new_content.splitlines(),
                    fromfile=f"previous/{file_path}",
                    tofile=f"current/{file_path}",
                    lineterm="",
                )
                diff = "\n".join(list(diff_lines))

                # Update snapshot to current content
                self.file_snapshots[file_path] = new_content

        # Record the change
        self.changes.append(
            ChangeRecord(
                agent_name=agent_name,
                timestamp=timestamp,
                file_path=file_path,
                change_description=change_description,
                diff=diff,
                details=details or {},
            )
        )

    def generate_documentation(self) -> str:
        """
        Generate comprehensive documentation of all changes.

        Returns:
            str: Markdown-formatted documentation
        """
        if not self.changes:
            return (
                "# DevGenius Change Documentation\n\nNo changes have been recorded yet."
            )

        # Group changes by agent
        changes_by_agent: Dict[str, List[ChangeRecord]] = {}
        for change in self.changes:
            if change.agent_name not in changes_by_agent:
                changes_by_agent[change.agent_name] = []
            changes_by_agent[change.agent_name].append(change)

        # Prepare prompt for GROQ
        prompt = self._prepare_documentation_prompt(changes_by_agent)

        # Send to GROQ
        messages = [
            {
                "role": "system",
                "content": "You are an expert technical documentation writer. Your task is to create clear, "
                "comprehensive documentation of changes made to a codebase by AI agents.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.groq_client.send_inference_request(
                model_id=self.config.model, input_data={"messages": messages}
            )

            # Extract documentation
            documentation = response.prediction.get("content", "")

            # Save documentation to file
            doc_filename = (
                f"changes-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            )
            doc_path = os.path.join(self.config.output_dir, doc_filename)

            with open(doc_path, "w") as f:
                f.write(documentation)

            return documentation

        except Exception as e:
            # Fallback to simple documentation if GROQ fails
            return self._generate_simple_documentation(changes_by_agent)

    def _prepare_documentation_prompt(
        self, changes_by_agent: Dict[str, List[ChangeRecord]]
    ) -> str:
        """Prepare prompt for documentation generation"""
        prompt = "I need documentation for the following changes made by AI agents to our codebase:\n\n"

        for agent_name, changes in changes_by_agent.items():
            prompt += f"## Changes by {agent_name}\n\n"

            for idx, change in enumerate(changes, 1):
                prompt += f"### Change {idx}: {change.file_path}\n"
                prompt += f"- Timestamp: {change.timestamp}\n"
                prompt += f"- Description: {change.change_description}\n"

                if change.details:
                    prompt += "- Details:\n"
                    for key, value in change.details.items():
                        prompt += f"  - {key}: {value}\n"

                if change.diff:
                    prompt += f"- Diff (truncated if long):\n```diff\n{change.diff[:500]}...\n```\n\n"

        prompt += """
                Please create comprehensive documentation from these changes with the following sections:
                1. Executive Summary - Brief overview of all changes
                2. Detailed Changes - Organized by agent, with technical details
                3. Impact Analysis - How these changes affect the system
                4. Recommendations - Suggestions for review or future improvements

                Format the documentation in Markdown with proper headings, code blocks, and formatting.
            """
        return prompt

    def _generate_simple_documentation(
        self, changes_by_agent: Dict[str, List[ChangeRecord]]
    ) -> str:
        """Generate simple documentation without using GROQ"""
        doc = "# DevGenius Change Documentation\n\n"
        doc += (
            f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        doc += "## Summary of Changes\n\n"
        doc += f"Total changes: {len(self.changes)}\n"
        doc += f"Agents involved: {', '.join(changes_by_agent.keys())}\n\n"

        for agent_name, changes in changes_by_agent.items():
            doc += f"## Changes by {agent_name}\n\n"

            for idx, change in enumerate(changes, 1):
                doc += f"### {idx}. {change.file_path}\n\n"
                doc += f"- **Timestamp**: {change.timestamp}\n"
                doc += f"- **Description**: {change.change_description}\n"

                if change.details:
                    doc += "- **Details**:\n"
                    for key, value in change.details.items():
                        doc += f"  - {key}: {value}\n"

                if change.diff:
                    doc += f"\n```diff\n{change.diff}\n```\n\n"

                doc += "\n"

        return doc
