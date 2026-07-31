import pytest
from fastapi import HTTPException

from src.core.settings import Settings, cors_config


class TestCorsConfig:
    def test_lista_tem_espacos_removidos(self):
        resultado = cors_config([" http://a.com ", "http://b.com "])
        assert resultado == ["http://a.com", "http://b.com"]

    def test_string_unica_vira_lista_com_um_item(self):
        resultado = cors_config("http://a.com")
        assert resultado == ["http://a.com"]

    def test_string_csv_e_separada_por_virgula(self):
        resultado = cors_config("http://a.com, http://b.com,http://c.com")
        assert resultado == ["http://a.com", "http://b.com", "http://c.com"]

    def test_string_com_colchetes_e_limpa(self):
        resultado = cors_config("[http://a.com, http://b.com]")
        assert resultado == ["http://a.com", "http://b.com"]

    def test_string_vazia_retorna_lista_vazia(self):
        assert cors_config("") == []

    def test_valor_nao_str_nem_lista_nao_lanca_e_retorna_none(self):
        # Bug conhecido: o branch `else` cria `ValueError(Urls)` mas nunca
        # dá `raise` nele, então a função apenas retorna None (implícito).
        resultado = cors_config(123)
        assert resultado is None


class TestSanatizeCors:
    def test_combina_hosts_com_commons_urls(self):
        settings = Settings(HOSTS="http://custom.com")

        resultado = settings.sanatize_cors

        # AnyUrl normaliza a URL adicionando "/" no final
        assert "http://custom.com/" in resultado
        for commons_url in settings.COMMONS_URLS:
            assert commons_url in resultado

    def test_hosts_vazio_retorna_so_commons_urls(self):
        settings = Settings(HOSTS=[])

        assert settings.sanatize_cors == settings.COMMONS_URLS


class TestPathValidator:
    def test_msg_path_none_levanta_http_500(self):
        # Bug conhecido: o field é tipado como `Path` (não opcional), então
        # pydantic nunca deixa None passar na construção. O branch só é
        # alcançável mutando o atributo direto após a instância existir.
        settings = Settings(MSG_PATH="Assets/mensagem.txt")
        settings.MSG_PATH = None

        with pytest.raises(HTTPException) as exc_info:
            settings.path_validator()

        assert exc_info.value.status_code == 500
        assert "MSG_PATH" in exc_info.value.detail

    def test_arquivo_inexistente_levanta_http_500(self):
        settings = Settings(MSG_PATH="/caminho/que/nao/existe.txt")

        with pytest.raises(HTTPException) as exc_info:
            settings.path_validator()

        assert exc_info.value.status_code == 500
        assert "Diretório não encontrado" in exc_info.value.detail

    def test_arquivo_valido_retorna_path(self, arquivo_template):
        settings = Settings(MSG_PATH=arquivo_template)

        resultado = settings.path_validator()

        assert str(resultado) == arquivo_template
