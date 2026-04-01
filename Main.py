# importação de bibliotecas

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings
from routes import Sender

# Carregamento de configurações básicas
app = FastAPI(
    title= settings.PROJECT_NAME,
    description= settings.DESCRIPTION
)

if settings.sanatize_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.sanatize_cors,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(Sender.routers)
