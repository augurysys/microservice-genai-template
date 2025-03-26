from fastapi import Depends

from core.llms.llm import BaseChain, LLMFactory
from utils.log_wrapper import LogWrapper
from models.generate_overview_request import GenerateFewShotsRequest


async def handle_generate_overview(g_request: GenerateFewShotsRequest,
                                   logger: LogWrapper,
                                   chain: BaseChain = Depends(LLMFactory.create_chain)) -> dict:
    logger.info("started handler handle_generate_overview", tags={"g_request": g_request})
    try:
        logger.info("finished generating", tags={"g_request": g_request, "result": "result"})
        return {}
    except Exception as e:
        logger.error("error while generating", tags={"g_request": g_request, "error": str(e)})
        raise e

