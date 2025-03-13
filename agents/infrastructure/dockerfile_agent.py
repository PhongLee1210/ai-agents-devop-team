from pydantic import BaseModel
from pydantic_ai import Agent
from models.groq_models import DockerConfig
from utils.groq_client import GROQClient
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()


class DockerfileConfig(BaseModel):
    """
    Configuration settings for the Dockerfile generator.

    Attributes:
        base_image (str): Base Docker image to use
        build_command (str): Command to build the application
        serve_command (str): Command to serve the application
        expose_port (int): Port to expose in the container
        copy_source (str): Source directory to copy
        work_dir (str): Working directory in the container
        groq_api_endpoint (str): GROQ API endpoint URL
        groq_api_key (str): Authentication key for GROQ API
    """

    base_image: str
    build_command: str
    serve_command: str
    expose_port: int
    copy_source: str
    work_dir: str
    groq_api_endpoint: str
    groq_api_key: str


class DockerfileAgent(Agent):
    """
    An AI agent that generates Docker configuration files.

    This agent can generate Dockerfiles for various application types,
    including React + Vite + TypeScript + Tailwind CSS applications.
    """

    def __init__(self, config: DockerfileConfig):
        """
        Initialize the Dockerfile agent with necessary configuration.

        Args:
            config (DockerfileConfig): Configuration for the Dockerfile
        """
        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )

    def fetch_config(self):
        """
        Fetch Dockerfile configuration from GROQ API.

        Queries the GROQ API for Docker configuration settings and updates
        the agent's configuration accordingly. Falls back to default values
        if the API request fails.
        """
        # Query GROQ API for Docker configuration
        groq_query = (
            "*[_type == 'dockerConfig'][0]{baseImage, exposePort, copySource, workDir}"
        )
        result = self.groq_client.query(groq_query)

        if result:
            # Update configuration with values from GROQ API
            self.config = DockerfileConfig(
                base_image=result.get("baseImage", "nginx:alpine"),
                expose_port=result.get("exposePort", 80),
                copy_source=result.get("copySource", "./html"),
                work_dir=result.get("workDir", "/usr/share/nginx/html"),
                groq_api_endpoint=result.get("groqApiEndpoint", ""),
                groq_api_key=result.get("groqApiKey", ""),
            )
        else:
            # Fallback to default configuration if API request fails
            self.config = DockerfileConfig()

    def generate_dockerfile(self, tech_stack: Dict[str, Any] = None) -> str:
        """
        Generate Dockerfile content based on the detected frontend tech stack.

        This method creates a multi-stage build Dockerfile that:
        1. Builds the frontend app with the appropriate build tool
        2. Creates a production-ready image
        3. Configures appropriate settings for performance

        Args:
            tech_stack (Dict[str, Any], optional): Detected tech stack information.
                If None, defaults to React + Vite + TypeScript.

        Returns:
            str: Complete Dockerfile content
        """
        # Default to React + Vite + TypeScript if no tech stack provided
        if tech_stack is None:
            tech_stack = {
                "framework": "React",
                "build_tool": "Vite",
                "css_framework": "Tailwind CSS",
                "typescript": True,
            }

        framework = tech_stack.get("framework", "React")
        build_tool = tech_stack.get("build_tool", "Vite")
        css_framework = tech_stack.get("css_framework", "Tailwind CSS")
        uses_typescript = tech_stack.get("typescript", True)

        # Generate appropriate build command based on the build tool
        build_command = self.config.build_command

        # Get the correct build output directory based on the build tool
        build_output_dir = "dist"
        if build_tool.lower() == "next.js":
            build_output_dir = ".next"
        elif build_tool.lower() == "angular":
            build_output_dir = "dist/frontend"
        elif build_tool.lower() == "webpack":
            build_output_dir = "dist"
        elif build_tool.lower() == "astro":
            build_output_dir = "dist"

        # Get the correct serve command/tool based on the framework and build tool
        serve_tool = "serve"
        serve_command = f"serve -s {build_output_dir} -l {self.config.expose_port}"

        if build_tool.lower() == "next.js":
            serve_tool = "next"
            serve_command = (
                "next start -p ${PORT:-" + str(self.config.expose_port) + "}"
            )
        elif build_tool.lower() == "angular":
            serve_tool = "angular-http-server"
            serve_command = f"angular-http-server --path {build_output_dir} -p {self.config.expose_port}"

        # Create the Dockerfile with appropriate comments
        dockerfile = f"""# Stage 1: Build the {framework} application with {build_tool}
FROM {self.config.base_image} as build

# Set working directory
WORKDIR {self.config.work_dir}

# Copy package.json and package-lock.json
COPY {self.config.copy_source}/package*.json ./

# Install dependencies
RUN npm ci

# Copy all frontend files
COPY {self.config.copy_source}/ ./

# Build the app
RUN {build_command}

# Stage 2: Setup production environment
FROM {self.config.base_image}

WORKDIR {self.config.work_dir}

# Install serve for a production server
RUN npm install -g {serve_tool}

# Copy build files from the previous stage
COPY --from=build {self.config.work_dir}/{build_output_dir} ./{build_output_dir}

# Set environment variables
ENV NODE_ENV=production

# Expose the port
EXPOSE {self.config.expose_port}

# Set the command to serve the app
CMD {serve_command}
"""
        return dockerfile

    def validate_dockerfile(self, dockerfile_content: str) -> bool:
        """
        Validate that the Dockerfile is correctly formatted.

        Args:
            dockerfile_content (str): Content of the Dockerfile to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Check for required elements
        required_elements = ["FROM", "WORKDIR", "COPY", "RUN", "EXPOSE", "CMD"]

        for element in required_elements:
            if element not in dockerfile_content:
                return False

        # Check for multi-stage build pattern
        if "FROM" not in dockerfile_content.split("\n")[0]:
            return False

        return True
