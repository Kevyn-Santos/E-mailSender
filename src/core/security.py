import time
from fastapi import Request, Security, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.settings import settings
import secrets, hashlib, sqlite3

# Dicionário compartilhado: IP -> timestamp de expiração do bloqueio
blocked_ips: dict[str, float] = {}

# Criar DbLocal
# Class APIKey
    ## Função criar uma APIKey
    ## Registrar ela num banco local
    ## Validar APIKey

# Criar um script para gerar as keys a partir do código
# Incluir retornos HTTP
# Definir onde no código as funções serão chamadas e executadas

class ApiKey:
    """Essa classe gerencia a criação, armazenamento e verificação das chaves API
    A cada instanciação da classe, uma nova conexão com o banco, 
    para aquela operação especifica será criada."""
    
    # inicializa o caminho do banco e a função de criação do banco a cada nova instancia da classe
    def __init__(self, path_db: str = "key.db"): 
        self._path_db = path_db 
        self.createDB()

    # Função que cria o banco de dados se ele não existir
    def createDB(self):
        with sqlite3.connect(self._path_db) as conn:
            conn.execute(f"""CREATE TABLE IF NOT EXISTS ApiKey(
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              key TEXT NOT NULL,
                              created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                              status INTEGER DEFAULT 1)""") 

    # Função que cria e hasheia as chaves de API
    def create_ApiKey(self) -> tuple[str, str]:
        rawKey = secrets.token_urlsafe()
        hashed = hashlib.sha256(rawKey.encode()).hexdigest()
        return (rawKey, hashed)
    
    # Função que armazena uma chave hasheada no banco
    def storeKey(self, hash_key: str) -> None:
        with sqlite3.connect(self._path_db) as conn:
            conn.execute("INSERT INTO ApiKey (key) VALUES(?)", (hash_key,))

    # Função que verifica se a chave esta no banco
    def verify_key(self, raw_key: str) -> bool:
        hashedKey = hashlib.sha256(raw_key.encode()).hexdigest() # Transforma a chave passada pelo usuário em Hex

        with sqlite3.connect(self._path_db) as conn: # Conecta com o banco
            result = conn.execute(
                "SELECT 1 FROM ApiKey WHERE key= ? LIMIT 1", (hashedKey,)
                ).fetchone() # Pede para o banco verificar e retornar 'True' na primeira instância encontrada da chave
            return result is not None # Retorna o valor da query

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
api_Key = ApiKey(path_db=str(settings.DB_PATH))


# Verifica se o front informou uma chave no campo 'X-API-Key'; retorna erro se o Header estiver ausente;
# _header_key = APIKeyHeader(name="X-API-Key", auto_error=True)
async def verify_header_key(key: str = settings.API_KEY) -> str: # Utiliza o módulo 'Security' para verificar a implantação da segurança utilizando os Escopos OAuth2.
    if not api_Key.verify_key(key):
        raise HTTPException(status_code=401, detail="Chave de API inválida ou inativa")
    return key