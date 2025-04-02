from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from api.handlers.support_response_handler import handle_generate_support_response
from core.llms.llm import BaseChain, LLMFactory
from models.generate_support_response_request import GenerateSupportResponseRequest

router = APIRouter(prefix="/support", tags=["support"])


@router.post("/generate/support_response")
async def generate_support_response(request: Request, g_request: GenerateSupportResponseRequest,
                                   chain: BaseChain = Depends(LLMFactory.create_chain)):
    """
    Generate support response
    """
    try:
        logger = request.state.logger
        tags = {}
        logger.info("started router support response", tags=tags)
        result = await handle_generate_support_response(g_request, logger, chain)
        logger.info("completed router support response", tags=tags)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
