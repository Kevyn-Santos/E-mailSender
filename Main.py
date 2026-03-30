# importação de bibliotecas

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings, cors_config
from routes.Sender import routers

# Carregamento de configurações básicas
app = FastAPI(
    title= settings.PROJECT_NAME,
    description= settings.DESCRIPTION
)

if settings.sanatize_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(routers)

print(f"""URL's tratadas: {settings.sanatize_cors}
URL's Comuns: {settings.COMMONS_URLS}
URL's Externas: {settings.HOSTS}
cors_config""" )


# if not all([Caminho_mensagem, me, passwd]): # validação de váriaveis de ambiente preenchidas
#        raise RuntimeError('Variaveis de ambiente SENDER, PASS ou MSG_PATH não definidas')
 
