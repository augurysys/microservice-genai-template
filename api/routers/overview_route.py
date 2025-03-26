from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException
from fastapi import Request

from api.handlers.overview_handler import handle_generate_overview
from models.generate_overview_request import GenerateFewShotsRequest

router = APIRouter(prefix="/overview", tags=["overview"])


@router.post("/generate")
async def generate_overview(request: Request, g_request: GenerateFewShotsRequest):
    """
    Generate result overview
    """
    try:
        logger = request.state.logger
        tags = {}
        logger.info("started router generate_overview", tags=tags)
        result = await handle_generate_overview(g_request, logger)
        logger.info("completed router generate_overview", tags=tags)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
