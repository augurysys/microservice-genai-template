from langchain_core.output_parsers import PydanticOutputParser
from core.few_shots_generator import FewShotsGenerator
from utils.log_wrapper import LogWrapper
from models.generate_support_response_request import GenerateSupportResponseRequest, SupportResponse

"""
 You can also load this from a json file also
"""
few_shots = [
    {
        "input": "Where is my order?",
        "output": "I’m sorry to hear that! Can you please provide your order ID so I can check the status for you?"
    },
    {
        "input": "I want to return a product",
        "output": "No problem! Can you share the order number and the reason for the return? I’ll guide you through the process."
    },
    {
        "input": "Do you offer international shipping?",
        "output": "Yes, we do ship internationally! Could you tell me your country so I can provide specific info?"
    },
    {
        "input": "How do I track my order?",
        "output": "You can track your order using the tracking link in your confirmation email. Let me know if you need help finding it!"
    },
    {
        "input": "I got the wrong item in my package.",
        "output": "I’m so sorry about that! Can you send a photo of what you received, along with your order ID? We'll get it sorted quickly."
    },
    {
        "input": "Can I change the delivery address?",
        "output": "If your order hasn’t shipped yet, we can update the address. Please share your order ID and the new address."
    },
    {
        "input": "Do you offer gift wrapping?",
        "output": "Yes, we do! You can select the gift wrap option during checkout. Would you like me to guide you through it?"
    },
    {
        "input": "Is this item in stock?",
        "output": "Let me check that for you! Which item are you referring to?"
    },
    {
        "input": "How long do refunds take?",
        "output": "Refunds typically take 5–7 business days to reflect on your original payment method after we receive the return."
    },
    {
        "input": "I used the wrong email at checkout.",
        "output": "No worries! Please provide the correct email and your order ID, and we’ll update it for you."
    }
]

base_prompt = ("You are a customer support agent for an e-commerce company. You are helping a customer with their "
               "queries.")


async def handle_generate_support_response(g_request: GenerateSupportResponseRequest,
                                           logger: LogWrapper, llm) -> dict:
    logger.info("started handler handle_generate_overview", tags={"g_request": g_request})
    try:
        parser = PydanticOutputParser(pydantic_object=SupportResponse)
        result = FewShotsGenerator(few_shots=few_shots, base_prompt=base_prompt,
                                   domain_data=g_request.domain_data, parser=parser,
                                   query=g_request.query, llm=llm, logger=logger).generate()
        logger.info("finished generating", tags={"g_request": g_request, "result": result})
        return result
    except Exception as e:
        logger.error("error while generating", tags={"g_request": g_request, "error": str(e)})
        raise e
