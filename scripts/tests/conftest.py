import os
import tempfile
import pytest

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
