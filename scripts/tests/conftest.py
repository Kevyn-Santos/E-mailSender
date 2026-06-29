import os
import tempfile
import pytest

# Deve ser definido ANTES de qualquer import de src.*,
# pois Settings() é instanciado no nível do módulo ao importar.
os.environ.setdefault("API_KEY", "chave-de-teste-unitario")

# DB_PATH padrão aponta para /app/data/key.db (caminho Docker).
# Em testes locais substituímos por um arquivo temporário real.
_db_temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_db_temp.close()
os.environ.setdefault("DB_PATH", _db_temp.name)

_TEMPLATE_CONTEUDO = "Olá {usuario}, seu e-mail é {email}."


# Arquivo de template temporário reutilizado em toda a sessão
@pytest.fixture(scope="session")
def arquivo_template():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as arquivo:
        arquivo.write(_TEMPLATE_CONTEUDO)
        caminho = arquivo.name
    yield caminho
    os.unlink(caminho)


# Banco de dados SQLite temporário por teste (isolamento total)
@pytest.fixture
def instancia_api_key():
    from src.core.security import ApiKey

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        caminho = tmp.name
    instancia = ApiKey(path_db=caminho)
    yield instancia
    os.unlink(caminho)
