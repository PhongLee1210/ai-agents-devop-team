import requests
from typing import Any, Dict
from pydantic import ValidationError
from models.groq_models import (
    InferenceRequest,
    InferenceResponse,
    CodeReviewRequest,
    CodeReviewFeedback,
    ChatCreateRequest,
    ChatCreateResponse,
    CodeIssue,
    CodeSuggestion,
)


class GROQClient:
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def send_inference_request(
        self, model_id: str, input_data: Dict[str, Any]
    ) -> InferenceResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model_id, "messages": input_data["messages"]}

        # TESTING: Log the request details
        print(f"Sending request to {self.api_endpoint}")
        print(f"Using model: {model_id}")

        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers)

            # TESTING: Log the response status
            print(f"Response status: {response.status_code}")

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                print(f"HTTP Error: {he}")
                print(f"Response text: {response.text}")
                raise
            # Parse the GROQ API response
            groq_response = response.json()

            # Transform the GROQ response to match our expected model
            # This assumes a standard structure from GROQ's chat completion API
            if "choices" in groq_response and len(groq_response["choices"]) > 0:
                message_content = (
                    groq_response["choices"][0].get("message", {}).get("content", "")
                )
                transformed_response = {
                    "prediction": {"content": message_content},
                    "confidence": 1.0,  # GROQ doesn't provide confidence, use default
                    "status": "success",
                }
                return InferenceResponse.parse_obj(transformed_response)
            else:
                # Handle empty or unexpected response
                return InferenceResponse(
                    prediction={"content": "No response from GROQ API"},
                    confidence=0.0,
                    status="error",
                )
        except ValidationError as e:
            print("Validation Error:", e)
            raise
        except Exception as e:
            print(f"Error processing GROQ response: {e}")
            # Return a structured error response rather than raising
            return InferenceResponse(
                prediction={"error": str(e)}, confidence=0.0, status="error"
            )

    def send_code_review_request(
        self, model_id: str, code_review_request: CodeReviewRequest
    ) -> CodeReviewFeedback:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": "You are a code review expert."},
                {
                    "role": "user",
                    "content": f"Review this code:\n```{code_review_request.code}```",
                },
            ],
        }

        # TESTING: Log the request details
        print(f"Sending code review request to {self.api_endpoint}")
        print(f"Using model: {model_id}")

        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers)

            # TESTING: Log the response status
            print(f"Response status: {response.status_code}")

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                print(f"HTTP Error: {he}")
                print(f"Response text: {response.text}")
                raise
            # Parse the GROQ API response
            groq_response = response.json()

            # Transform the GROQ response to match our expected CodeReviewFeedback model
            if "choices" in groq_response and len(groq_response["choices"]) > 0:
                feedback_content = (
                    groq_response["choices"][0].get("message", {}).get("content", "")
                )

                # Parse the feedback content to extract issues and suggestions
                # This is a simplified version - you might need more sophisticated parsing
                transformed_response = {
                    "issues": [{"description": feedback_content, "severity": "info"}],
                    "suggestions": [
                        {"description": "See above feedback", "priority": "medium"}
                    ],
                    "overall_quality": "needs_review",
                }
                return CodeReviewFeedback.parse_obj(transformed_response)
            else:
                # Handle empty response
                return CodeReviewFeedback(
                    issues=[
                        CodeIssue(
                            description="No response from GROQ API", severity="error"
                        )
                    ],
                    suggestions=[],
                    overall_quality="needs_review",
                )
        except ValidationError as e:
            print("Validation Error:", e)
            raise
        except Exception as e:
            print(f"Error processing GROQ response: {e}")
            return CodeReviewFeedback(
                issues=[CodeIssue(description=f"Error: {str(e)}", severity="error")],
                suggestions=[],
                overall_quality="needs_review",
            )

    # New Method for Chat-Create API
    def send_chat_create_request(
        self, chat_create_request: ChatCreateRequest
    ) -> ChatCreateResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": chat_create_request.model_id,
            "messages": [
                {"role": "system", "content": chat_create_request.context},
                {"role": "user", "content": chat_create_request.user_message},
            ],
        }

        # TESTING: Log the request details
        print(f"Sending chat request to {self.api_endpoint}")
        print(f"Using model: {chat_create_request.model_id}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers)

            # TESTING: Log the response status
            print(f"Response status: {response.status_code}")

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                print(f"HTTP Error: {he}")
                print(f"Response text: {response.text}")
                raise
            # Parse the GROQ API response
            groq_response = response.json()

            # Transform the GROQ response to match our expected ChatCreateResponse model
            if "choices" in groq_response and len(groq_response["choices"]) > 0:
                message_content = (
                    groq_response["choices"][0].get("message", {}).get("content", "")
                )
                transformed_response = {
                    "response": message_content,
                    "metadata": {
                        "model": groq_response.get("model", ""),
                        "usage": groq_response.get("usage", {}),
                    },
                }
                return ChatCreateResponse.parse_obj(transformed_response)
            else:
                # Handle empty response
                return ChatCreateResponse(
                    response="No response from GROQ API",
                    metadata={"error": "Empty response"},
                )
        except ValidationError as e:
            print("Validation Error:", e)
            raise
        except Exception as e:
            print(f"Error processing GROQ response: {e}")
            return ChatCreateResponse(
                response=f"Error: {str(e)}", metadata={"error": str(e)}
            )
