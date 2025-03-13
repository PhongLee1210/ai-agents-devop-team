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
        # DEBUGGING: Print and verify the API endpoint
        print(f"GROQClient initialized with endpoint: {api_endpoint}")
        # Remove any trailing slashes to ensure consistent URL formation
        if self.api_endpoint.endswith("/"):
            self.api_endpoint = self.api_endpoint.rstrip("/")
        self.api_key = api_key

    def send_inference_request(
        self, model_id: str, input_data: Dict[str, Any]
    ) -> InferenceResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Enhance the system message if it exists with frontend-focused DevOps expertise
        messages = input_data["messages"]
        if len(messages) > 0 and messages[0].get("role") == "system":
            # Enhance existing system message with frontend-specific DevOps expertise
            original_content = messages[0].get("content", "")
            enhanced_content = f"{original_content}\n\nYou are an expert in frontend development and DevOps for frontend applications. You understand modern JavaScript frameworks, build tools, and frontend deployment pipelines. You can identify and solve issues related to frontend performance, bundle optimization, and CI/CD workflows for web applications."
            messages[0]["content"] = enhanced_content

        payload = {"model": model_id, "messages": messages}

        # Ensure correct API endpoint
        endpoint = self.api_endpoint
        if "openai/v1/chat/completions" not in endpoint:
            # Start with a clean base URL without trailing slash
            if endpoint.endswith("/"):
                endpoint = endpoint.rstrip("/")

            # Add the correct path
            endpoint = f"{endpoint}/openai/v1/chat/completions"

        print(f"Using endpoint URL: {endpoint}")

        # TESTING: Log the request details
        print(f"Sending request to {endpoint}")
        print(f"Using model: {model_id}")

        try:
            response = requests.post(endpoint, json=payload, headers=headers)

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

        # Create a frontend-focused code review system prompt
        system_prompt = """You are a frontend code review expert specializing in modern web development.

Your expertise includes:
1. Modern JavaScript/TypeScript frameworks (React, Vue, Angular, Svelte)
2. Frontend build tools and bundlers (Webpack, Vite, Rollup)
3. CSS frameworks and methodologies (Tailwind, SCSS, CSS Modules, styled-components)
4. Frontend performance optimization and best practices
5. Web accessibility standards and implementation
6. Frontend testing strategies (unit, integration, E2E tests)
7. Frontend CI/CD pipelines and deployment workflows

When reviewing frontend code, focus on:
- Component structure and reusability
- State management approaches
- Responsive design implementation
- Browser compatibility considerations
- Frontend performance optimizations
- Build configuration improvements

Provide actionable, specific feedback that improves both code quality and the developer experience."""

        # Create a more detailed and structured user prompt specifically for frontend code
        user_prompt = f"""Review the following frontend code:

```
{code_review_request.code}
```

File: {code_review_request.file_name}
Language: {code_review_request.language}

Consider:
- Component architecture and reusability
- Performance and optimization opportunities
- UI/UX implementation quality
- Build and deployment considerations
- Frontend testing approach
- Modern frontend best practices

Structure your review with:
1. Overall assessment of code quality
2. Key issues that should be addressed
3. Specific improvement suggestions
4. Best practices to consider"""

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        # Ensure correct API endpoint
        endpoint = self.api_endpoint
        if "openai/v1/chat/completions" not in endpoint:
            # Start with a clean base URL without trailing slash
            if endpoint.endswith("/"):
                endpoint = endpoint.rstrip("/")

            # Add the correct path
            endpoint = f"{endpoint}/openai/v1/chat/completions"

        print(f"Using endpoint URL: {endpoint}")

        # TESTING: Log the request details
        print(f"Sending code review request to {endpoint}")
        print(f"Using model: {model_id}")

        try:
            response = requests.post(endpoint, json=payload, headers=headers)

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

        # Enhance the system context with frontend-specific DevOps expertise
        enhanced_context = chat_create_request.context
        if "You are a helpful AI assistant" in enhanced_context:
            enhanced_context = """You are a specialized frontend DevOps assistant with expertise in:

1. Frontend build systems (Webpack, Vite, Rollup, esbuild)
2. Frontend testing automation (Jest, Testing Library, Cypress, Playwright)
3. Frontend CI/CD pipelines optimized for web applications
4. Static site deployment and hosting solutions
5. Frontend performance monitoring and optimization
6. JavaScript/TypeScript bundling, minification, and optimization
7. Asset optimization for web delivery
8. Frontend-specific Docker configurations
9. CDN configuration and edge deployments
10. Progressive Web App (PWA) implementation and delivery

You provide practical guidance on developing, testing, and deploying modern frontend applications using DevOps principles. Your recommendations focus on improving developer experience, build performance, and deployment efficiency for web applications."""

        payload = {
            "model": chat_create_request.model_id,
            "messages": [
                {"role": "system", "content": enhanced_context},
                {"role": "user", "content": chat_create_request.user_message},
            ],
        }

        # Ensure correct API endpoint
        endpoint = self.api_endpoint
        if "openai/v1/chat/completions" not in endpoint:
            # Start with a clean base URL without trailing slash
            if endpoint.endswith("/"):
                endpoint = endpoint.rstrip("/")

            # Add the correct path
            endpoint = f"{endpoint}/openai/v1/chat/completions"

        print(f"Using endpoint URL: {endpoint}")

        # TESTING: Log the request details
        print(f"Sending chat request to {endpoint}")
        print(f"Using model: {chat_create_request.model_id}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(endpoint, json=payload, headers=headers)

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
