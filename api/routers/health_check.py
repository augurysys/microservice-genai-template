from fastapi.responses import JSONResponse
from fastapi import APIRouter

router = APIRouter(prefix="")


@router.get("/_ping", tags=["root"])
async def health_check():
    return JSONResponse({"status": "OK"})
