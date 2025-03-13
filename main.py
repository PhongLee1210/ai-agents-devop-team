from agents.ci_cd.github_actions_agent import GitHubActionsAgent, GitHubActionsConfig
from agents.infrastructure.dockerfile_agent import DockerfileAgent, DockerfileConfig
from agents.analysis.build_predictor_agent import (
    BuildPredictorAgent,
    BuildPredictorConfig,
)
from agents.infrastructure.build_status_agent import BuildStatusAgent, BuildStatusConfig
from agents.analysis.tech_stack_agent import TechStackAgent, TechStackConfig
from agents.documentation.documentation_agent import (
    DocumentationAgent,
    DocumentationConfig,
)
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main orchestration function that coordinates the DevOps AI team's activities.

    This function manages six main tasks:
    1. Analyze the frontend tech stack
    2. Creating a GitHub Actions CI/CD pipeline customized for the detected frontend framework
    3. Generating a Dockerfile tailored for the specific frontend framework and build tool
    4. Building and checking Docker image status
    5. Predicting build success/failure based on the detected frontend tech stack
    6. Document all changes made by the AI agents
    """
    print("🤖 DevGenius DevOps AI Team Starting Up...")

    # Initialize documentation agent first to track all changes
    doc_config = DocumentationConfig(
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        output_dir="docs",
    )
    doc_agent = DocumentationAgent(config=doc_config)

    # 1. Analyze Tech Stack
    print("\n1️⃣ Tech Stack Agent: Analyzing frontend technologies...")
    tech_config = TechStackConfig(
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        frontend_dir="frontend",
    )
    tech_agent = TechStackAgent(config=tech_config)

    # Analyze tech stack and get results
    tech_stack = tech_agent.detect_tech_stack()
    print(f"📊 Detected Tech Stack: {tech_stack}")

    # Extract key tech stack information for easier reference
    framework = tech_stack.get("framework", "React")
    build_tool = tech_stack.get("build_tool", "Vite")
    css_framework = tech_stack.get("css_framework", "Tailwind CSS")
    uses_typescript = tech_stack.get("typescript", True)

    # Record this in documentation
    doc_agent.record_change(
        agent_name="TechStackAgent",
        file_path="frontend/",
        change_description="Analyzed frontend tech stack",
        details=tech_stack,
    )

    # 2. Create GitHub Actions Pipeline based on detected tech stack
    print(
        f"\n2️⃣ GitHub Actions Agent: Creating CI/CD Pipeline for {framework} with {build_tool}..."
    )
    # Take snapshot of existing file if it exists
    workflow_file = ".github/workflows/frontend-ci.yml"
    doc_agent.record_file_snapshot(workflow_file)

    gha_config = GitHubActionsConfig(
        workflow_name=f"{framework} {build_tool} CI Pipeline",
        node_version=tech_stack.get("node_version", "18.x"),
        python_version="3.13.0",
        run_tests=True,
        run_linting=True,
        build_frontend=True,
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    gha_agent = GitHubActionsAgent(config=gha_config)
    # Pass the tech stack to generate a customized pipeline
    pipeline = gha_agent.generate_pipeline(tech_stack=tech_stack)

    # Ensure the directory exists
    os.makedirs(".github/workflows", exist_ok=True)

    # Save the pipeline configuration to a YAML file
    with open(workflow_file, "w") as f:
        f.write(pipeline)
    print(f"✅ {framework} CI/CD Pipeline created!")

    # Record the change
    doc_agent.record_change(
        agent_name="GitHubActionsAgent",
        file_path=workflow_file,
        change_description=f"Created CI/CD pipeline for {framework} with {build_tool}",
        details={"framework": framework, "build_tool": build_tool},
    )

    # 3. Create Dockerfile tailored for the detected tech stack
    print(
        f"\n3️⃣ Dockerfile Agent: Creating Dockerfile for {framework} with {build_tool}..."
    )
    # Take snapshot
    doc_agent.record_file_snapshot("Dockerfile")

    docker_config = DockerfileConfig(
        base_image="node:18-alpine",  # Lightweight Node.js image
        build_command="npm run build",  # Default build command
        serve_command="npm run preview",  # Default serve command
        expose_port=4173,  # Default port
        copy_source="./frontend",  # Source directory for frontend
        work_dir="/app",  # Working directory in container
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    docker_agent = DockerfileAgent(config=docker_config)
    # Pass the tech stack to generate a customized Dockerfile
    dockerfile = docker_agent.generate_dockerfile(tech_stack=tech_stack)

    # Save the Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print(f"✅ Dockerfile created for {framework} with {build_tool}!")

    # Record the change
    doc_agent.record_change(
        agent_name="DockerfileAgent",
        file_path="Dockerfile",
        change_description=f"Created Dockerfile for {framework} application with {build_tool}",
        details={
            "framework": framework,
            "build_tool": build_tool,
            "base_image": "node:18-alpine",
            "expose_port": 4173,
        },
    )

    # 4. Build and Check Status
    print(
        f"\n4️⃣ Build Status Agent: Building and checking Docker image for {framework}..."
    )
    status_config = BuildStatusConfig(image_tag="devgenius-frontend:latest")
    status_agent = BuildStatusAgent(config=status_config)

    # Attempt to build the Docker image
    print(f"🔨 Building Docker image for {framework}...")
    import subprocess

    build_result = subprocess.run(
        ["docker", "build", "-t", "devgenius-frontend:latest", "."],
        capture_output=True,  # Capture command output
        text=True,  # Return string instead of bytes
    )

    # Verify the build status
    status = status_agent.check_build_status()
    print(f"📊 Build Status: {status}")

    # Record the change
    doc_agent.record_change(
        agent_name="BuildStatusAgent",
        file_path="Docker Image",
        change_description=f"Built and verified Docker image for {framework}",
        details={
            "status": status,
            "image_tag": "devgenius-frontend:latest",
            "framework": framework,
        },
    )

    # 5. Predict Build Success/Failure based on detected tech stack
    print(
        f"\n5️⃣ Build Predictor Agent: Analyzing build patterns for {framework} with {build_tool}..."
    )
    predictor_config = BuildPredictorConfig(
        model="llama3-8b-8192",  # Using Groq's recommended model
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    predictor_agent = BuildPredictorAgent(config=predictor_config)

    # Prepare build data for analysis
    build_data = {
        "dockerfile_exists": True,  # Dockerfile was created
        "ci_pipeline_exists": True,  # CI pipeline was created
        "last_build_status": status,  # Result of the latest build
        "node_version": tech_stack.get("node_version", "18.x"),
        "typescript_version": tech_stack.get("typescript_version", "^5.0.0"),
        "dependencies_updated": True,
    }

    # Get build prediction using the tech stack
    prediction = predictor_agent.predict_build_failure(
        build_data, tech_stack=tech_stack
    )
    print(f"🔮 Build Prediction: {prediction}")

    # Record the prediction
    doc_agent.record_change(
        agent_name="BuildPredictorAgent",
        file_path="Build Analysis",
        change_description=f"Predicted build outcome for {framework} with {build_tool}",
        details={
            "prediction": prediction,
            "build_data": build_data,
            "tech_stack": tech_stack,
        },
    )

    # 6. Generate Documentation
    print("\n6️⃣ Documentation Agent: Generating change documentation...")
    documentation = doc_agent.generate_documentation()
    print(f"📝 Documentation created and saved to the docs directory")

    print(
        f"\n✨ DevGenius DevOps AI Team has completed their tasks for {framework} with {build_tool}!"
    )


if __name__ == "__main__":
    main()
