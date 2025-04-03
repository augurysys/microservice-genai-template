from pydantic import BaseModel, Field


class GenerateSupportResponseRequest(BaseModel):
    domain_data: str
    query: str


class SupportResponse(BaseModel):
    response: str = Field(..., description="Answer to the customer query")
    action_required: bool = Field(..., description="True if human action is needed")
