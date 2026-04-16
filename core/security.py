import time
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.settings import settings

# Dicionário compartilhado: IP -> timestamp de expiração do bloqueio
blocked_ips: dict[str, float] = {}

# Limiter com Sliding Window real (moving-window)
limiter = Limiter(
    key_func=get_remote_address,
    strategy="moving-window",
)

def get_rate_limit_string() -> str:
    return f"{settings.QTD_EMAILS}/{settings.TMP_EMAILS} seconds"

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    client_ip = get_remote_address(request)
    blocked_ips[client_ip] = time.time() + settings.TMP_BLOQ

    response = JSONResponse(
        content={
            "error": "Muitas requisições",
            "detail": (
                f'Limite de tentativas excedido. Tente novamente em {settings.TMP_BLOQ} segundos.'
                #f"Limite de {settings.QTD_EMAILS} emails por {settings.TMP_EMAILS}s excedido. "
                #f"IP bloqueado por {settings.TMP_BLOQ} segundos."
            )
        },
        status_code=429,
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response


# --- JWT ---

_bearer_scheme = HTTPBearer()


class Jwt:
    @staticmethod
    def create_token(data: dict) -> str:
        payload = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload.update({"exp": expire})
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)]
    ) -> dict:
        return Jwt.verify_token(credentials.credentials)
