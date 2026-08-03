from email.mime.multipart import MIMEMultipart
from smtplib import SMTPAuthenticationError, SMTPConnectError
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.core.mail_config import ResolvedMailConfig

_TEMPLATE_CONTEUDO = "Olá {usuario}, seu e-mail é {email}."


def _criar_config(template=_TEMPLATE_CONTEUDO) -> ResolvedMailConfig:
    return ResolvedMailConfig(
        sender="remetente@teste.com",
        password="senha-fake",
        smtp_server="smtp.fake.com",
        port_smtp=465,
        ehelo="localhost",
        subject="Assunto de Teste",
        template=template,
    )


class TestBuildMail:
    def test_retorna_mime_multipart(self):
        from src.services.sendMail import buildMail

        mensagem = buildMail(to="destino@teste.com", name="Usuário Teste", config=_criar_config())
        assert isinstance(mensagem, MIMEMultipart)

    def test_cabecalho_from_correto(self):
        from src.services.sendMail import buildMail

        config = _criar_config()
        mensagem = buildMail(to="destino@teste.com", name="Usuário Teste", config=config)
        assert mensagem["from"] == config.sender

    def test_cabecalho_to_correto(self):
        from src.services.sendMail import buildMail

        mensagem = buildMail(to="destino@teste.com", name="Usuário Teste", config=_criar_config())
        assert mensagem["to"] == "destino@teste.com"

    def test_cabecalho_subject_correto(self):
        from src.services.sendMail import buildMail

        config = _criar_config()
        mensagem = buildMail(to="destino@teste.com", name="Usuário Teste", config=config)
        assert mensagem["subject"] == config.subject

    def test_corpo_substitui_placeholders(self):
        from src.services.sendMail import buildMail

        mensagem = buildMail(to="destino@teste.com", name="Carlos", config=_criar_config())
        payload = mensagem.get_payload(0).get_payload(decode=True).decode("utf-8")  # type: ignore
        assert "Carlos" in payload
        assert "destino@teste.com" in payload

    def test_template_com_variavel_invalida_levanta_key_error(self):
        from src.services.sendMail import buildMail

        config = _criar_config(template="Olá {variavel_inexistente}.")
        with pytest.raises(KeyError):
            buildMail(to="a@b.com", name="Alguém", config=config)


class TestSendMail:
    def test_envia_mensagem_com_sucesso(self):
        from src.services.sendMail import sendMail

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            sendMail(to="destino@teste.com", name="Usuário", config=_criar_config())

        mock_smtp.send_message.assert_called_once()

    def test_smtp_connect_error_levanta_http_500(self):
        from src.services.sendMail import sendMail

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(side_effect=SMTPConnectError(421, b"falha"))
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            with pytest.raises(HTTPException) as exc_info:
                sendMail(to="destino@teste.com", name="Usuário", config=_criar_config())

        assert exc_info.value.status_code == 500
        assert "SMTP" in exc_info.value.detail

    def test_smtp_auth_error_levanta_http_500(self):
        from src.services.sendMail import sendMail

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(
            side_effect=SMTPAuthenticationError(535, b"credenciais invalidas")
        )
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            with pytest.raises(HTTPException) as exc_info:
                sendMail(to="destino@teste.com", name="Usuário", config=_criar_config())

        assert exc_info.value.status_code == 500
        assert (
            "autenticação" in exc_info.value.detail.lower()
            or "smtp" in exc_info.value.detail.lower()
        )

    def test_template_com_variavel_invalida_levanta_http_500(self):
        # buildMail roda dentro do try/except do SMTP em sendMail,
        # então o KeyError de template inválido vira HTTPException 500.
        from src.services.sendMail import sendMail

        config = _criar_config(template="Olá {variavel_inexistente}.")

        with pytest.raises(HTTPException) as exc_info:
            sendMail(to="destino@teste.com", name="Usuário", config=config)

        assert exc_info.value.status_code == 500
        assert "variavel_inexistente" in exc_info.value.detail
