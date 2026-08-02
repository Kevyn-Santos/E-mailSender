# importação de bibliotecas

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from src.core.security import Rate_limiter
from src.core.settings import settings
from src.routes import Health, Sender

# Carregamento de configurações básicas
app = FastAPI(title=settings.PROJECT_NAME, description=settings.DESCRIPTION)

# Registra o limiter e o handler de rate limit
app.state.limiter = Rate_limiter.limiter
app.add_exception_handler(RateLimitExceeded, Rate_limiter.rate_limit_exceeded_handler)  # type: ignore

if settings.sanatize_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins= "*" if settings.DEBUG else settings.sanatize_cors,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(Sender.routers)
app.include_router(Health.router)
