from pydantic import BaseModel
from pydantic_ai import Agent
from utils.groq_client import GROQClient


class GitHubActionsConfig(BaseModel):
    """
    Configuration settings for the GitHub Actions workflow generator.

    Attributes:
        workflow_name (str): Name of the GitHub Actions workflow
        node_version (str): Node.js version to use in the pipeline
        python_version (str): Python version to use in the pipeline
        run_tests (bool): Whether to run tests in the pipeline
        run_linting (bool): Whether to run linting in the pipeline
        build_frontend (bool): Whether to build the frontend in the pipeline
        groq_api_endpoint (str): GROQ API endpoint URL
        groq_api_key (str): Authentication key for GROQ API
    """

    workflow_name: str
    node_version: str = "18.x"
    python_version: str
    run_tests: bool = True
    run_linting: bool = True
    build_frontend: bool = True
    groq_api_endpoint: str
    groq_api_key: str


class GitHubActionsAgent(Agent):
    """
    An AI agent that generates and manages GitHub Actions workflows.

    This agent can fetch configuration from GROQ's API and generate
    appropriate GitHub Actions workflow files with CI/CD pipeline definitions.
    """

    def __init__(self, config: GitHubActionsConfig):
        """
        Initialize the GitHub Actions agent with necessary configuration.

        Args:
            config (GitHubActionsConfig): Configuration object containing workflow settings
        """
        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )

    def fetch_config(self):
        """
        Fetch workflow configuration from GROQ API.

        Queries the GROQ API for GitHub Actions configuration settings and updates
        the agent's configuration accordingly. Falls back to default values
        if the API request fails.
        """
        groq_query = "*[_type == 'githubActionConfig'][0]{workflowName, nodeVersion, pythonVersion, runTests, runLinting, buildFrontend}"
        result = self.groq_client.query(groq_query)
        if result:
            # Update configuration with values from GROQ API
            self.config = GitHubActionsConfig(
                workflow_name=result.get("workflowName", "Frontend CI Pipeline"),
                node_version=result.get("nodeVersion", "18.x"),
                python_version=result.get("pythonVersion", "3.13.0"),
                run_tests=result.get("runTests", True),
                run_linting=result.get("runLinting", True),
                build_frontend=result.get("buildFrontend", True),
                groq_api_endpoint=result.get("groqApiEndpoint", ""),
                groq_api_key=result.get("groqApiKey", ""),
            )
        else:
            # Fallback to default configuration if API request fails
            self.config = GitHubActionsConfig()

    def generate_pipeline(self) -> str:
        """
        Generate GitHub Actions workflow YAML content.

        Creates a complete CI/CD pipeline definition including:
        - Node.js and Python setup
        - Frontend dependencies installation
        - TypeScript linting
        - React component testing
        - Vite build process
        - Docker configuration and container testing
        - Environment variable handling
        - Caching for improved performance

        Returns:
            str: Complete GitHub Actions workflow YAML content
        """
        pipeline = f"""
name: {self.config.workflow_name}

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  pull-requests: write

jobs:
  frontend-ci:
    runs-on: ubuntu-latest
    
    env:
      GROQ_API_ENDPOINT: ${{{{ secrets.GROQ_API_ENDPOINT }}}}  # API endpoint for GROQ
      GROQ_API_KEY: ${{{{ secrets.GROQ_API_KEY }}}}           # Authentication key
      GITHUB_TOKEN: ${{{{ secrets.GH_TOKEN }}}}               # GitHub access token

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Node.js {self.config.node_version}
      uses: actions/setup-node@v3
      with:
        node-version: {self.config.node_version}
        cache: 'npm'
        cache-dependency-path: '**/package-lock.json'

    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Cache Node modules
      uses: actions/cache@v3
      with:
        path: ~/.npm
        key: ${{{{ runner.os }}}}-node-${{{{ hashFiles('**/package-lock.json') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-node-
"""

        # Add linting step if configured
        if self.config.run_linting:
            pipeline += """
    - name: Lint TypeScript code
      working-directory: ./frontend
      run: npm run lint
"""

        # Add testing step if configured
        if self.config.run_tests:
            pipeline += """
    - name: Run frontend tests
      working-directory: ./frontend
      run: npm test
"""

        # Add build step if configured
        if self.config.build_frontend:
            pipeline += """
    - name: Build frontend
      working-directory: ./frontend
      run: npm run build
"""

        # Add Python setup for backend/DevOps tasks
        pipeline += f"""
    - name: Set up Python {self.config.python_version}
      uses: actions/setup-python@v4
      with:
        python-version: {self.config.python_version}

    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-pip-

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Run DevOps AI Team
      run: |
        python main.py

    - name: Build and start Docker Container
      run: |
        docker build -t devgenius-frontend:latest .
        docker run -d -p 4173:4173 devgenius-frontend:latest
        sleep 5  # Give container a moment to start

    - name: Test Docker Container
      run: |
        if docker ps | grep -q devgenius-frontend; then
          echo "🔍 Testing Docker container endpoints..."
          
          if curl -I http://localhost:4173/ | grep -q "200 OK"; then
            echo "✅ React app home page test passed! 🚀"
          else
            echo "❌ React app home page test failed 😢"
            exit 1
          fi
          
          if curl -I http://localhost:4173/about | grep -q "200 OK"; then
            echo "✅ About page test passed! 🎯"
          else
            echo "❌ About page test failed 😢"
            exit 1
          fi
          
          echo "🎉 All Docker container tests passed successfully! 🌟"
        else
          echo "⚠️ Docker container not running, skipping tests 🤔"
          exit 1
        fi
        """

        return pipeline
