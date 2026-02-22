import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int) -> None:
        super().__init__(app)
        self.limit = limit_per_minute
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        now = time.time()
        ip = request.client.host if request.client else "unknown"
        window = self.hits[ip]

        while window and now - window[0] > 60:
            window.popleft()

        if len(window) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        window.append(now)
        return await call_next(request)
