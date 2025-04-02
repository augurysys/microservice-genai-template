from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from openai import BaseModel
from pydantic import Field

from core.few_shots_generator import FewShotsGenerator
from core.llms.llm import BaseChain
from utils.log_wrapper import LogWrapper
from models.generate_support_response_request import GenerateSupportResponseRequest

"""
 You can also load this from a json file also
"""
few_shots = [
    {
        "query": "Where is my order?",
        "answer": "I’m sorry to hear that! Can you please provide your order ID so I can check the status for you?"
    },
    {
        "query": "I want to return a product",
        "answer": "No problem! Can you share the order number and the reason for the return? I’ll guide you through the process."
    },
    {
        "query": "Do you offer international shipping?",
        "answer": "Yes, we do ship internationally! Could you tell me your country so I can provide specific info?"
    },
    {
        "query": "How do I track my order?",
        "answer": "You can track your order using the tracking link in your confirmation email. Let me know if you need help finding it!"
    },
    {
        "query": "I got the wrong item in my package.",
        "answer": "I’m so sorry about that! Can you send a photo of what you received, along with your order ID? We'll get it sorted quickly."
    },
    {
        "query": "Can I change the delivery address?",
        "answer": "If your order hasn’t shipped yet, we can update the address. Please share your order ID and the new address."
    },
    {
        "query": "Do you offer gift wrapping?",
        "answer": "Yes, we do! You can select the gift wrap option during checkout. Would you like me to guide you through it?"
    },
    {
        "query": "Is this item in stock?",
        "answer": "Let me check that for you! Which item are you referring to?"
    },
    {
        "query": "How long do refunds take?",
        "answer": "Refunds typically take 5–7 business days to reflect on your original payment method after we receive the return."
    },
    {
        "query": "I used the wrong email at checkout.",
        "answer": "No worries! Please provide the correct email and your order ID, and we’ll update it for you."
    }
]

base_prompt = ("You are a customer support agent for an e-commerce company. You are helping a customer with their "
               "queries.")


class SupportResponse(BaseModel):
    response: str = Field(..., description="Answer to the customer query")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level in the response")
    action_required: bool = Field(..., description="True if human action is needed")


async def handle_generate_support_response(g_request: GenerateSupportResponseRequest,
                                           logger: LogWrapper, chain: BaseChain) -> dict:
    logger.info("started handler handle_generate_overview", tags={"g_request": g_request})
    try:
        parser = PydanticOutputParser(pydantic_object=SupportResponse)
        result = FewShotsGenerator(few_shots=few_shots, base_prompt=base_prompt,
                                   domain_data=g_request.domain_data, parser=parser,
                                   query=g_request.query, llm=chain, logger=logger).generate()
        logger.info("finished generating", tags={"g_request": g_request, "result": result})
        return result
    except Exception as e:
        logger.error("error while generating", tags={"g_request": g_request, "error": str(e)})
        raise e
