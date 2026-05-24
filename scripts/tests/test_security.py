import asyncio
import hashlib
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


class TestApiKeyCreacao:
    def test_retorna_par_de_strings(self, instancia_api_key):
        chave_bruta, hash_ = instancia_api_key.create_ApiKey()
        assert isinstance(chave_bruta, str)
        assert isinstance(hash_, str)

    def test_chave_bruta_difere_do_hash(self, instancia_api_key):
        chave_bruta, hash_ = instancia_api_key.create_ApiKey()
        assert chave_bruta != hash_

    def test_hash_e_sha256_valido(self, instancia_api_key):
        chave_bruta, hash_ = instancia_api_key.create_ApiKey()
        esperado = hashlib.sha256(chave_bruta.encode()).hexdigest()
        assert hash_ == esperado

    def test_chaves_consecutivas_sao_unicas(self, instancia_api_key):
        chave1, _ = instancia_api_key.create_ApiKey()
        chave2, _ = instancia_api_key.create_ApiKey()
        assert chave1 != chave2


class TestApiKeyArmazenamento:
    def test_chave_armazenada_e_verificada(self, instancia_api_key):
        chave_bruta, hash_ = instancia_api_key.create_ApiKey()
        instancia_api_key.storeKey(hash_)
        assert instancia_api_key.verify_key(chave_bruta) is True

    def test_chave_nao_armazenada_retorna_falso(self, instancia_api_key):
        chave_bruta, _ = instancia_api_key.create_ApiKey()
        assert instancia_api_key.verify_key(chave_bruta) is False

    def test_string_invalida_retorna_falso(self, instancia_api_key):
        assert instancia_api_key.verify_key("chave-invalida-qualquer") is False

    def test_string_vazia_retorna_falso(self, instancia_api_key):
        assert instancia_api_key.verify_key("") is False

    def test_multiplas_chaves_verificadas_independentemente(self, instancia_api_key):
        chave1, hash1 = instancia_api_key.create_ApiKey()
        chave2, hash2 = instancia_api_key.create_ApiKey()
        instancia_api_key.storeKey(hash1)

        assert instancia_api_key.verify_key(chave1) is True
        assert instancia_api_key.verify_key(chave2) is False


class TestApiKeyBancoDados:
    def test_tabela_criada_na_inicializacao(self, instancia_api_key):
        import sqlite3
        with sqlite3.connect(instancia_api_key._path_db) as conn:
            tabelas = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ApiKey'"
            ).fetchone()
        assert tabelas is not None

    def test_banco_criado_duas_vezes_nao_gera_erro(self, instancia_api_key):
        # createDB é idempotente (CREATE TABLE IF NOT EXISTS)
        instancia_api_key.createDB()


class TestVerifyHeaderKey:
    def _criar_mock_api_key(self, retorno_verify: bool) -> MagicMock:
        mock = MagicMock()
        mock.verify_key.return_value = retorno_verify
        return mock

    def test_chave_valida_retorna_a_chave(self):
        mock_api_key = self._criar_mock_api_key(retorno_verify=True)
        with patch("src.core.security.api_Key", mock_api_key):
            from src.core.security import verify_header_key
            resultado = asyncio.run(verify_header_key(key="chave-valida"))
        assert resultado == "chave-valida"

    def test_chave_invalida_levanta_401(self):
        mock_api_key = self._criar_mock_api_key(retorno_verify=False)
        with patch("src.core.security.api_Key", mock_api_key):
            from src.core.security import verify_header_key
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(verify_header_key(key="chave-invalida"))
        assert exc_info.value.status_code == 401
