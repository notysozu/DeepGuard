from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api_gateway.app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)



def require_auth(
    creds: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> None:
    if creds is None or creds.scheme.lower() != "bearer" or creds.credentials != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
        )
