from pydantic import BaseModel
from pydantic_ai import Agent
from utils.groq_client import GROQClient
from typing import Dict, Any


# Configuration class for the BuildPredictor agent
class BuildPredictorConfig(BaseModel):
    """
    Configuration settings for the Build Predictor agent.

    Attributes:
        model (str): Model ID for GROQ inference
        groq_api_endpoint (str): GROQ API endpoint URL
        groq_api_key (str): Authentication key for GROQ API
    """

    model: str
    groq_api_endpoint: str
    groq_api_key: str


class BuildPredictorAgent(Agent):
    """
    An AI agent that predicts build success or failure for React + Vite + TypeScript + Tailwind CSS applications.

    This agent uses GROQ's large language models to analyze build patterns
    and predict whether a build will succeed or fail based on various factors
    such as dependency versions, code linting, TypeScript errors, and more.
    """

    def __init__(self, config: BuildPredictorConfig):
        """
        Initialize the Build Predictor agent with necessary configuration.

        Args:
            config (BuildPredictorConfig): Configuration for the predictor
        """
        # TESTING: Always use static values for CI testing
        print("Using static GROQ_API_ENDPOINT for testing")
        config.groq_api_endpoint = "https://api.groq.com/openai/v1/chat/completions"

        print("Using static GROQ_API_KEY for testing")
        config.groq_api_key = "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"

        # Always use llama3-8b-8192 model as specified
        print("Using specified model ID: llama3-8b-8192")
        config.model = "llama3-8b-8192"

        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )

    def predict_build_failure(
        self, build_data: Dict[str, Any], tech_stack: Dict[str, Any] = None
    ) -> str:
        """
        Predict whether a build will fail or succeed based on the provided data.

        This method analyzes various frontend-specific factors based on the detected
        tech stack and other build environment data.

        Args:
            build_data (Dict[str, Any]): Data about the build including environment,
                                         dependencies, and previous build status
            tech_stack (Dict[str, Any], optional): Detected tech stack information.
                If None, defaults to React + Vite + TypeScript.

        Returns:
            str: Prediction of build success or failure with reasoning
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

        # Format the build data for the prompt
        build_context = "\n".join(
            [f"- {key}: {value}" for key, value in build_data.items()]
        )

        # Add the tech stack information to the build context
        tech_stack_context = "\n".join(
            [f"- {key}: {value}" for key, value in tech_stack.items()]
        )

        # Create a framework-agnostic prompt for the GROQ model
        prompt = f"""
As an AI build prediction expert, analyze the following data about a frontend project and predict whether the next build will succeed or fail.

Frontend Tech Stack:
{tech_stack_context}

Build Environment Data:
{build_context}

Consider the following factors in your analysis:
1. Are there any incompatibilities between the Node.js version and the detected framework/libraries?
2. Are there version compatibility issues between the frontend framework and its dependencies?
"""

        # Add framework-specific considerations
        if framework.lower() == "react":
            prompt += """
3. Are there potential issues with React component rendering or hooks?
4. Could there be problems with JSX syntax or React-specific patterns?
"""
        elif framework.lower() == "vue":
            prompt += """
3. Are there potential issues with Vue component structure or lifecycle hooks?
4. Could there be problems with Vue templates or directives?
"""
        elif framework.lower() == "angular":
            prompt += """
3. Are there potential issues with Angular modules, components, or services?
4. Could there be problems with dependency injection or Angular decorators?
"""
        elif framework.lower() == "svelte":
            prompt += """
3. Are there potential issues with Svelte component structure or reactivity?
4. Could there be problems with Svelte's compile-time framework approach?
"""

        # Add build tool-specific considerations
        if build_tool.lower() == "vite":
            prompt += """
5. Are there potential issues with Vite's configuration or plugin system?
6. Could there be problems with Vite's ES modules approach?
"""
        elif build_tool.lower() == "webpack":
            prompt += """
5. Are there potential issues with Webpack's configuration or loaders?
6. Could there be problems with code splitting or bundle optimization?
"""
        elif build_tool.lower() == "next.js":
            prompt += """
5. Are there potential issues with Next.js routing or server-side rendering?
6. Could there be problems with Next.js API routes or data fetching methods?
"""

        # Add CSS framework-specific considerations
        if css_framework.lower() == "tailwind css":
            prompt += """
7. Are there potential issues with Tailwind CSS configuration or plugin system?
8. Could there be problems with PurgeCSS or Tailwind's utility-first approach?
"""
        elif css_framework.lower() == "bootstrap":
            prompt += """
7. Are there potential issues with Bootstrap components or grid system?
8. Could there be problems with Bootstrap's JavaScript dependencies?
"""
        elif css_framework.lower() == "scss" or css_framework.lower() == "sass":
            prompt += """
7. Are there potential issues with SCSS/SASS compilation or variables?
8. Could there be problems with SCSS/SASS import structure or mixins?
"""

        # Add TypeScript-specific considerations if applicable
        if uses_typescript:
            prompt += """
9. Are there TypeScript compilation errors or type definition issues?
10. Could there be problems with TypeScript configuration or strict mode settings?
"""

        # Add the standard format request
        prompt += """
Format your response as follows:
PREDICTION: [SUCCESS/FAILURE]
CONFIDENCE: [percentage]
REASONING: [detailed explanation of your prediction]
RECOMMENDATIONS: [suggestions to prevent build failure if applicable]
"""

        # Send to GROQ
        messages = [
            {
                "role": "system",
                "content": f"You are an AI build prediction expert specialized in {framework} projects with {build_tool}. You analyze build data and predict outcomes.",
            },
            {"role": "user", "content": prompt},
        ]

        # Make the API request
        try:
            response = self.groq_client.send_inference_request(
                model_id=self.config.model, input_data={"messages": messages}
            )
            # Extract and return the prediction
            return response.prediction.get("content", "Failed to predict build outcome")
        except Exception as e:
            return f"Error making prediction: {str(e)}"
