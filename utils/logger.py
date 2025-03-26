import sys
import json

import logging
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid


class LogLevelFilter(logging.Filter):
    def __init__(self, handler_log_levels):
        super(LogLevelFilter, self).__init__()
        self.handler_log_levels = handler_log_levels

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno in self.handler_log_levels:
            return True
        return False


def get_logger(name, log_level: int or None = None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        if not log_level:
            log_level = logging.INFO
        logger.setLevel(log_level)
        logger.propagate = False
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # Error handler
        error_handler = logging.StreamHandler(stream=sys.stderr)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        error_filter = LogLevelFilter(handler_log_levels=[logging.ERROR, logging.CRITICAL])
        error_handler.addFilter(filter=error_filter)
        # Info handler
        info_handler = logging.StreamHandler(stream=sys.stdout)
        info_handler.setFormatter(formatter)
        info_handler.setLevel(logging.INFO)
        info_filter = LogLevelFilter(handler_log_levels=[logging.INFO, logging.WARNING])
        info_handler.addFilter(filter=info_filter)
        # Debug handler
        debug_handler = logging.StreamHandler(stream=sys.stdout)
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        debug_filter = LogLevelFilter(handler_log_levels=[logging.DEBUG, logging.NOTSET])
        debug_handler.addFilter(filter=debug_filter)
        # Add handlers
        logger.addHandler(error_handler)
        logger.addHandler(info_handler)
        logger.addHandler(debug_handler)
    return logger


class LogRequestMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            logger,
    ):
        super().__init__(app)
        self.logger = logger
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.disabled = True
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.disabled = True

    async def dispatch(self, request: Request, call_next):
        request.state.logger = self.logger
        start_time = datetime.now()
        method = request.scope['method']
        path = request.scope['path']
        req_id = uuid.uuid4().hex[:12]
        request.state.req_id = req_id
        tags = {"method": method, "path": path, "req_id": req_id}
        if not self.metrics_or_health_request(method, path):
            self.logger.info(f"[START]", tags=tags)
            try:
                self.logger.info("LogRequestMiddleware start")
                body = json.loads(request.state.cached_body)
                print("LogRequestMiddleware after body")
                self.logger.info(f"[RequestBody]", tags={"req_id": req_id, "body": body})
            except Exception as e:
                self.logger.debug("request without body", tags={"req_id": req_id})

        response = await call_next(request)

        req_time = int((datetime.now() - start_time).total_seconds() * 1000)

        tags.update({"status_code": response.status_code, "duration": req_time})
        if hasattr(request.state, 'user'):
            tags.update(request.state.user.dict(exclude_none=True))
        if not self.metrics_or_health_request(method, path):
            self.logger.info(f"[FINISH]", tags=tags)
        self.logger.info("LogRequestMiddleware finish")
        return response

    @staticmethod
    def metrics_or_health_request(method, path):
        if method == "GET" and path == "/metrics":
            return True
        if method == "GET" and path == "/_ping":
            return True
        return False
