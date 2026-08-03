from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.settings import settings


class Ratelimiter:
    # Limiter com Sliding Window real (moving-window).
    # storage_uri controla onde a contagem de requisições é guardada.
    # settings.RATE_LIMIT_STORAGE_URI usa "memory://" por padrão (em processo,
    # não sobrevive a reinícios nem é compartilhado entre réplicas).
    #
    # Para persistir a contagem entre deploys/réplicas, trocar por Redis
    # (requer o pacote `limits[redis]` e um serviço Redis disponível —
    # ainda não incluído no projeto):
    #
    # limiter = Limiter(
    #     key_func=get_remote_address,
    #     strategy="moving-window",
    #     storage_uri="redis://redis:6379/0",
    # )
    limiter = Limiter(
        key_func=get_remote_address,
        strategy="moving-window",
        storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    )
    
    def get_rate_limit_string(self) -> str:
        return f"{settings.QTD_EMAILS}/{settings.TMP_EMAILS} seconds"

    def rate_limit_exceeded_handler(
        self, request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        response = JSONResponse(
            content={
                "error": "Muitas requisições",
                "detail": "Limite de tentativas excedido. Tente novamente em instantes.",
            },
            status_code=429,
        )
        response = request.app.state.limiter._inject_headers(
            response, request.state.view_rate_limit
        )
        return response


Rate_limiter = Ratelimiter()
