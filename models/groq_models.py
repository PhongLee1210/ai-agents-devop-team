from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class GitHubAction(BaseModel):
    name: str
    steps: List[str]


class DockerConfig(BaseModel):
    base_image: str
    expose_port: int
    copy_source: str
    work_dir: str


class InferenceRequest(BaseModel):
    model_id: str
    input_data: Dict[str, Any]


class InferenceResponse(BaseModel):
    prediction: Dict[str, Any]
    confidence: float
    status: str


# New Models for Code Review
class CodeReviewRequest(BaseModel):
    code: str
    file_name: Optional[str] = None
    language: Optional[str] = None


class CodeIssue(BaseModel):
    description: str
    severity: str  # "error", "warning", "info"


class CodeSuggestion(BaseModel):
    description: str
    priority: str  # "high", "medium", "low"


class CodeReviewFeedback(BaseModel):
    issues: List[CodeIssue]
    suggestions: List[CodeSuggestion]
    overall_quality: str  # "good", "needs_improvement", "needs_review"


# New Models for Chat-Create API
class ChatCreateRequest(BaseModel):
    model_id: str
    user_message: str
    context: str = "You are a helpful AI assistant."


class ChatCreateResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]
