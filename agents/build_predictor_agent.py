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
        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )

    def predict_build_failure(self, build_data: Dict[str, Any]) -> str:
        """
        Predict whether a build will fail or succeed based on the provided data.

        This method analyzes various frontend-specific factors including:
        - TypeScript version compatibility
        - React dependency issues
        - Vite build configuration
        - Tailwind CSS setup
        - Node.js version compatibility

        Args:
            build_data (Dict[str, Any]): Data about the build including environment,
                                         dependencies, and previous build status

        Returns:
            str: Prediction of build success or failure with reasoning
        """
        # Format the build data for the prompt
        build_context = "\n".join(
            [f"- {key}: {value}" for key, value in build_data.items()]
        )

        # Create the prompt for the GROQ model
        prompt = f"""
As an AI build prediction expert, analyze the following data about a React + Vite + TypeScript + Tailwind CSS frontend project and predict whether the next build will succeed or fail.

Build Environment Data:
{build_context}

Consider the following factors in your analysis:
1. Are there any incompatibilities between the Node.js version and other dependencies?
2. Is the TypeScript version compatible with the React version?
3. Are there potential issues with the Vite configuration?
4. Could there be Tailwind CSS integration problems?
5. What is the likelihood of test failures based on the current status?

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
                "content": "You are an AI build prediction expert. You analyze build data and predict outcomes.",
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
