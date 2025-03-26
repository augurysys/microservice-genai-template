from pydantic import BaseModel


class GenerateFewShotsRequest(BaseModel):
    base_prompt: str
    few_shots: list
    domain_data: str
    output_instructions: str
    query: str
