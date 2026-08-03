import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from email_sender_sdk import EmailSenderClient


class TestEmailSenderClientPayload:
    def test_campos_none_sao_omitidos_do_payload(self):
        client = EmailSenderClient(base_url="http://api.teste")

        mock_response = MagicMock()
        with patch("email_sender_sdk.client.httpx.post", return_value=mock_response) as mock_post:
            client.send(user_mail="a@b.com", user_name="Fulano")

        _, kwargs = mock_post.call_args
        assert "config" not in kwargs["json"]

    def test_campos_informados_vao_no_payload(self):
        client = EmailSenderClient(
            base_url="http://api.teste",
            sender="dev@exemplo.com",
            password="senha",
            subject="Assunto",
            template="Olá {usuario}",
        )

        mock_response = MagicMock()
        with patch("email_sender_sdk.client.httpx.post", return_value=mock_response) as mock_post:
            client.send(user_mail="a@b.com", user_name="Fulano")

        _, kwargs = mock_post.call_args
        assert kwargs["json"]["config"] == {
            "sender": "dev@exemplo.com",
            "password": "senha",
            "subject": "Assunto",
            "template": "Olá {usuario}",
        }
        assert kwargs["json"]["userMail"] == "a@b.com"
        assert kwargs["json"]["userName"] == "Fulano"

    def test_base_url_com_barra_final_e_normalizada(self):
        client = EmailSenderClient(base_url="http://api.teste/")

        mock_response = MagicMock()
        with patch("email_sender_sdk.client.httpx.post", return_value=mock_response) as mock_post:
            client.send(user_mail="a@b.com", user_name="Fulano")

        args, _ = mock_post.call_args
        assert args[0] == "http://api.teste/sendMail"

    def test_erro_http_propaga_excecao(self):
        import httpx

        client = EmailSenderClient(base_url="http://api.teste")

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "erro", request=MagicMock(), response=MagicMock()
        )
        with patch("email_sender_sdk.client.httpx.post", return_value=mock_response):
            with pytest.raises(httpx.HTTPStatusError):
                client.send(user_mail="a@b.com", user_name="Fulano")


class TestEmailSenderClientTemplatePath:
    def test_template_path_e_lido_e_vira_template(self, tmp_path):
        arquivo = tmp_path / "template.txt"
        arquivo.write_text("Olá {usuario}, bem-vindo!", encoding="utf-8")

        client = EmailSenderClient(base_url="http://api.teste", template_path=arquivo)

        assert client._config["template"] == "Olá {usuario}, bem-vindo!"

    def test_template_explicito_e_template_path_juntos_prevalece_arquivo(self, tmp_path):
        arquivo = tmp_path / "template.txt"
        arquivo.write_text("Conteúdo do arquivo", encoding="utf-8")

        client = EmailSenderClient(
            base_url="http://api.teste",
            template="Conteúdo inline (ignorado)",
            template_path=arquivo,
        )

        assert client._config["template"] == "Conteúdo do arquivo"


class TestEmailSenderClientFromEnv:
    def test_from_env_le_variaveis_com_prefixo(self, monkeypatch):
        monkeypatch.setenv("EMAIL_SENDER_SENDER", "dev@exemplo.com")
        monkeypatch.setenv("EMAIL_SENDER_PASSWORD", "senha")
        monkeypatch.setenv("EMAIL_SENDER_SUBJECT", "Assunto")
        monkeypatch.setenv("EMAIL_SENDER_PORT_SMTP", "465")

        client = EmailSenderClient.from_env(base_url="http://api.teste")

        assert client._config["sender"] == "dev@exemplo.com"
        assert client._config["password"] == "senha"
        assert client._config["subject"] == "Assunto"
        assert client._config["port_smtp"] == 465

    def test_from_env_sem_variaveis_definidas_gera_config_vazia(self, monkeypatch):
        for chave in (
            "EMAIL_SENDER_SENDER",
            "EMAIL_SENDER_PASSWORD",
            "EMAIL_SENDER_SMTP_SERVER",
            "EMAIL_SENDER_PORT_SMTP",
            "EMAIL_SENDER_EHELO",
            "EMAIL_SENDER_SUBJECT",
            "EMAIL_SENDER_TEMPLATE",
            "EMAIL_SENDER_TEMPLATE_PATH",
        ):
            monkeypatch.delenv(chave, raising=False)

        client = EmailSenderClient.from_env(base_url="http://api.teste")

        assert all(valor is None for valor in client._config.values())
