# importação de bibliotecas

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.core.settings import settings
from src.core.security import Rate_limiter, blocked_ips
from src.routes import Sender
from src.routes import Health

# Carregamento de configurações básicas
app = FastAPI(
    title= settings.PROJECT_NAME,
    description= settings.DESCRIPTION
)

# Registra o limiter e o handler de rate limit
app.state.limiter = Rate_limiter.limiter
app.add_exception_handler(RateLimitExceeded, Rate_limiter.rate_limit_exceeded_handler)  # type: ignore

if settings.sanatize_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.sanatize_cors,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Middleware de bloqueio de IP — adicionado por último = executado primeiro
@app.middleware("http")
async def block_banned_ips(request: Request, call_next):
    client_ip = request.client.host if request.client else None
    if client_ip:
        expiry = blocked_ips.get(client_ip)
        if expiry is not None:
            if time.time() < expiry:
                remaining = int(expiry - time.time())
                return JSONResponse(
                    content={
                        "error": "IP bloqueado",
                        "detail": f"Tente novamente em {remaining} segundos."
                    },
                    status_code=429,
                )
            else:
                del blocked_ips[client_ip]

    return await call_next(request)

app.include_router(Sender.routers)
app.include_router(Health.router)
