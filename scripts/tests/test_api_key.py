# import sys, os
# print("CWD:", os.getcwd())
# print("Sistema: ", sys.path[:3])

import pytest
import tempfile
import os
from src.core.security import ApiKey


@pytest.fixture
def chaves():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        caminho = tmp.name
    instancia = ApiKey(path_db=caminho)
    yield instancia
    os.unlink(caminho)


def test_criar_chave_retorna_par(chaves):
    chave_bruta, hash_ = chaves.create_ApiKey()
    assert isinstance(chave_bruta, str) and isinstance(hash_, str)
    assert chave_bruta != hash_


def test_armazenar_e_verificar(chaves):
    chave_bruta, hash_ = chaves.create_ApiKey()
    chaves.storeKey(hash_)
    assert chaves.verify_key(chave_bruta) is True


def test_chave_invalida(chaves):
    assert chaves.verify_key("qualquer-coisa") is False


def test_chave_nao_armazenada(chaves):
    chave_bruta, _ = chaves.create_ApiKey()
    assert chaves.verify_key(chave_bruta) is False  # gerada mas não salva
