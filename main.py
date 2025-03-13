from agents.github_actions_agent import GitHubActionsAgent, GitHubActionsConfig
from agents.dockerfile_agent import DockerfileAgent, DockerfileConfig
from agents.build_predictor_agent import BuildPredictorAgent, BuildPredictorConfig
from agents.build_status_agent import BuildStatusAgent, BuildStatusConfig
from agents.tech_stack_agent import TechStackAgent, TechStackConfig
from agents.documentation_agent import DocumentationAgent, DocumentationConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main orchestration function that coordinates the DevOps AI team's activities.

    This function manages six main tasks:
    1. Analyze the frontend tech stack
    2. Creating a GitHub Actions CI/CD pipeline for React + Vite + TypeScript + Tailwind CSS
    3. Generating a Dockerfile for the frontend application
    4. Building and checking Docker image status
    5. Predicting build success/failure for the frontend
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

    # Record this in documentation
    doc_agent.record_change(
        agent_name="TechStackAgent",
        file_path="frontend/",
        change_description="Analyzed frontend tech stack",
        details=tech_stack,
    )

    # 2. Create GitHub Actions Pipeline
    print(
        "\n2️⃣ GitHub Actions Agent: Creating CI/CD Pipeline for React + Vite + TypeScript..."
    )
    # Take snapshot of existing file if it exists
    workflow_file = ".github/workflows/frontend-ci.yml"
    doc_agent.record_file_snapshot(workflow_file)

    gha_config = GitHubActionsConfig(
        workflow_name="Frontend CI Pipeline",
        node_version=tech_stack.get("node_version", "18.x"),
        python_version="3.13.0",
        run_tests=True,
        run_linting=True,
        build_frontend=True,
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    gha_agent = GitHubActionsAgent(config=gha_config)
    pipeline = gha_agent.generate_pipeline()

    # Ensure the directory exists
    os.makedirs(".github/workflows", exist_ok=True)

    # Save the pipeline configuration to a YAML file
    with open(workflow_file, "w") as f:
        f.write(pipeline)
    print("✅ CI/CD Pipeline created!")

    # Record the change
    doc_agent.record_change(
        agent_name="GitHubActionsAgent",
        file_path=workflow_file,
        change_description="Created CI/CD pipeline for frontend",
        details={
            "framework": tech_stack.get("framework", "React"),
            "build_tool": tech_stack.get("build_tool", "Vite"),
        },
    )

    # 3. Create Dockerfile
    print("\n3️⃣ Dockerfile Agent: Creating Dockerfile for React + Vite + TypeScript...")
    # Take snapshot
    doc_agent.record_file_snapshot("Dockerfile")

    docker_config = DockerfileConfig(
        base_image="node:18-alpine",  # Lightweight Node.js image
        build_command="npm run build",  # Vite build command
        serve_command="npm run preview",  # Vite preview command
        expose_port=4173,  # Default Vite preview port
        copy_source="./frontend",  # Source directory for frontend
        work_dir="/app",  # Working directory in container
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    docker_agent = DockerfileAgent(config=docker_config)
    dockerfile = docker_agent.generate_dockerfile()

    # Save the Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print("✅ Dockerfile created!")

    # Record the change
    doc_agent.record_change(
        agent_name="DockerfileAgent",
        file_path="Dockerfile",
        change_description="Created Dockerfile for frontend application",
        details={"base_image": "node:18-alpine", "expose_port": 4173},
    )

    # 4. Build and Check Status
    print("\n4️⃣ Build Status Agent: Building and checking Docker image...")
    status_config = BuildStatusConfig(image_tag="devgenius-frontend:latest")
    status_agent = BuildStatusAgent(config=status_config)

    # Attempt to build the Docker image
    print("🔨 Building Docker image...")
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
        change_description="Built and verified Docker image",
        details={"status": status, "image_tag": "devgenius-frontend:latest"},
    )

    # 5. Predict Build Success/Failure
    print(
        "\n5️⃣ Build Predictor Agent: Analyzing build patterns for React + Vite + TypeScript..."
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
        "typescript_version": tech_stack.get("typescript", "^5.0.0"),
        "framework": tech_stack.get("framework", "React"),
        "framework_version": tech_stack.get("framework_version", "^18.2.0"),
        "build_tool": tech_stack.get("build_tool", "Vite"),
        "build_tool_version": tech_stack.get("build_tool_version", "^4.4.0"),
        "css_framework": tech_stack.get("css_framework", "Tailwind CSS"),
        "css_framework_version": tech_stack.get("css_framework_version", "^3.3.0"),
        "dependencies_updated": True,
    }

    # Get build prediction
    prediction = predictor_agent.predict_build_failure(build_data)
    print(f"🔮 Build Prediction: {prediction}")

    # Record the prediction
    doc_agent.record_change(
        agent_name="BuildPredictorAgent",
        file_path="Build Analysis",
        change_description="Predicted build outcome",
        details={"prediction": prediction, "build_data": build_data},
    )

    # 6. Generate Documentation
    print("\n6️⃣ Documentation Agent: Generating change documentation...")
    documentation = doc_agent.generate_documentation()
    print(f"📝 Documentation created and saved to the docs directory")

    print("\n✨ DevGenius DevOps AI Team has completed their tasks!")


if __name__ == "__main__":
    main()
