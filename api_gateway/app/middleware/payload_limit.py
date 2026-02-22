from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_payload_mb: int) -> None:
        super().__init__(app)
        self.max_bytes = max_payload_mb * 1024 * 1024

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_bytes:
            return JSONResponse(status_code=413, content={"detail": "Payload too large"})
        return await call_next(request)
