import time
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from core.settings import settings

# Dicionário compartilhado: IP -> timestamp de expiração do bloqueio
blocked_ips: dict[str, float] = {}


class Ratelimiter:

    # Limiter com Sliding Window real (moving-window)
    limiter = Limiter(
        key_func=get_remote_address,
        strategy="moving-window",
    )

    def get_rate_limit_string(self) -> str:
        return f"{settings.QTD_EMAILS}/{settings.TMP_EMAILS} seconds"

    def rate_limit_exceeded_handler(self, request: Request, exc: RateLimitExceeded) -> JSONResponse:
        client_ip = get_remote_address(request)
        blocked_ips[client_ip] = time.time() + settings.TMP_BLOQ

        response = JSONResponse(
            content={
                "error": "Muitas requisições",
                "detail": (
                    f'Limite de tentativas excedido. Tente novamente em {settings.TMP_BLOQ} segundos.'
                )
            },
            status_code=429,
        )
        response = request.app.state.limiter._inject_headers(
            response, request.state.view_rate_limit
        )
        return response

Rate_limiter = Ratelimiter()