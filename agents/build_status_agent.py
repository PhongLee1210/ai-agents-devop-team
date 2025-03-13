from pydantic import BaseModel
from pydantic_ai import Agent
import subprocess
import re
from typing import Dict, Any, List, Optional


class BuildStatusConfig(BaseModel):
    """
    Configuration settings for the Build Status agent.

    Attributes:
        image_tag (str): Docker image tag for the frontend application
        port (int): Port to check for the running application
    """

    image_tag: str
    port: int = 4173  # Default port for Vite preview


class BuildStatusAgent(Agent):
    """
    An AI agent that checks the status of React + Vite + TypeScript + Tailwind CSS application builds.

    This agent verifies whether the application has been built successfully and is running properly
    in a Docker container, including checks for the Vite development server, TypeScript compilation,
    and proper rendering of React components.
    """

    def __init__(self, config: BuildStatusConfig):
        """
        Initialize the Build Status agent with necessary configuration.

        Args:
            config (BuildStatusConfig): Configuration for the status agent
        """
        super().__init__()
        self.config = config

    def check_build_status(self) -> str:
        """
        Check the status of the Docker image build and container.

        This method verifies:
        1. If the Docker image exists and was built successfully
        2. If a container using that image is currently running
        3. If the container's health status is good

        Returns:
            str: Status message indicating "success" or "failure" and additional details
        """
        # Check if the Docker image exists
        image_exists = self._check_if_image_exists()
        if not image_exists:
            return "failure: Docker image not found"

        # Check if a container is running with this image
        container_id = self._get_running_container_id()
        if not container_id:
            return "failure: No running container found"

        # Check container health
        container_health = self._check_container_health(container_id)
        if container_health != "healthy":
            return f"failure: Container health check failed - {container_health}"

        # Check if the application port is responding
        port_check = self._check_port_responding()
        if not port_check:
            return f"failure: Application not responding on port {self.config.port}"

        return "success: Build and container running properly"

    def _check_if_image_exists(self) -> bool:
        """Check if the Docker image exists"""
        result = subprocess.run(
            ["docker", "images", "-q", self.config.image_tag],
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())

    def _get_running_container_id(self) -> Optional[str]:
        """Get the ID of a running container using the image"""
        result = subprocess.run(
            ["docker", "ps", "-q", "--filter", f"ancestor={self.config.image_tag}"],
            capture_output=True,
            text=True,
        )
        container_id = result.stdout.strip()
        return container_id if container_id else None

    def _check_container_health(self, container_id: str) -> str:
        """Check the health status of a container"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    container_id,
                ],
                capture_output=True,
                text=True,
            )
            health = result.stdout.strip()
            return health if health else "health check not configured"
        except:
            # If health check is not configured, check if container is running
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Status}}", container_id],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()

    def _check_port_responding(self) -> bool:
        """Check if the application is responding on the expected port"""
        try:
            # Use curl to check if the port is responding with HTTP 200
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    f"http://localhost:{self.config.port}",
                ],
                capture_output=True,
                text=True,
            )
            status_code = result.stdout.strip()
            return status_code == "200"
        except:
            return False

    def get_vite_build_logs(self) -> List[str]:
        """
        Retrieve the Vite build logs from the container.

        Returns:
            List[str]: List of log lines from the Vite build process
        """
        container_id = self._get_running_container_id()
        if not container_id:
            return ["No running container found"]

        result = subprocess.run(
            ["docker", "logs", container_id], capture_output=True, text=True
        )

        # Extract Vite/TypeScript build related logs
        logs = result.stdout.split("\n")
        build_logs = [
            log
            for log in logs
            if any(
                term in log.lower()
                for term in [
                    "vite",
                    "typescript",
                    "tsx",
                    "build",
                    "error",
                    "warning",
                    "bundle",
                ]
            )
        ]

        return build_logs if build_logs else ["No Vite build logs found"]
