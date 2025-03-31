from pydantic import BaseModel


class GenerateSupportResponseRequest(BaseModel):
    domain_data: str
    query: str
