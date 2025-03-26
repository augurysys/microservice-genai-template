from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message


class CacheRequestBodyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        # Cache the body
        self.logger.info("CacheRequestBodyMiddleware start")
        # assuming we don't have large body
        # otherwise, consider improving this by using _receive
        body = await request.body()
        async def receive() -> Message:
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive

        try:
            request.state.cached_body = body
        except Exception as e:
            print(f"Error while caching request body: {e}")

        response = await call_next(request)
        self.logger.info("CacheRequestBodyMiddleware finish")
        return response
