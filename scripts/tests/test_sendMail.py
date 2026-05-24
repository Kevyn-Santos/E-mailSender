import pytest
from unittest.mock import patch, MagicMock, mock_open
from smtplib import SMTPConnectError, SMTPAuthenticationError
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException


# Configurações simuladas injetadas nos módulos de serviço
_SETTINGS_FAKE = {
    "SENDER": "remetente@teste.com",
    "SUBJECT": "Assunto de Teste",
    "SMTP_SERVER": "smtp.fake.com",
    "PORT_SMTP": 465,
    "EHELO": "localhost",
    "PASS": "senha-falsa",
}


def _criar_mock_settings(path_valido=None):
    mock = MagicMock()
    mock.SENDER = _SETTINGS_FAKE["SENDER"]
    mock.SUBJECT = _SETTINGS_FAKE["SUBJECT"]
    mock.SMTP_SERVER = _SETTINGS_FAKE["SMTP_SERVER"]
    mock.PORT_SMTP = _SETTINGS_FAKE["PORT_SMTP"]
    mock.EHELO = _SETTINGS_FAKE["EHELO"]
    mock.PASS = _SETTINGS_FAKE["PASS"]
    mock.path_validator.return_value = path_valido
    return mock


class TestBuildMail:
    def test_retorna_mime_multipart(self, arquivo_template):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings(arquivo_template)):
            mensagem = buildMail(
                to="destino@teste.com", name="Usuário Teste", path=arquivo_template
            )
        assert isinstance(mensagem, MIMEMultipart)

    def test_cabecalho_from_correto(self, arquivo_template):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings(arquivo_template)):
            mensagem = buildMail(
                to="destino@teste.com", name="Usuário Teste", path=arquivo_template
            )
        assert mensagem["from"] == _SETTINGS_FAKE["SENDER"]

    def test_cabecalho_to_correto(self, arquivo_template):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings(arquivo_template)):
            mensagem = buildMail(
                to="destino@teste.com", name="Usuário Teste", path=arquivo_template
            )
        assert mensagem["to"] == "destino@teste.com"

    def test_cabecalho_subject_correto(self, arquivo_template):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings(arquivo_template)):
            mensagem = buildMail(
                to="destino@teste.com", name="Usuário Teste", path=arquivo_template
            )
        assert mensagem["subject"] == _SETTINGS_FAKE["SUBJECT"]

    def test_corpo_substitui_placeholders(self, arquivo_template):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings(arquivo_template)):
            mensagem = buildMail(
                to="destino@teste.com", name="Carlos", path=arquivo_template
            )
        payload = mensagem.get_payload(0).get_payload(decode=True).decode("utf-8")
        assert "Carlos" in payload
        assert "destino@teste.com" in payload

    def test_arquivo_inexistente_levanta_file_not_found(self):
        from src.services.sendMail import buildMail

        with patch("src.services.sendMail.settings", _criar_mock_settings()):
            with pytest.raises(FileNotFoundError):
                buildMail(
                    to="a@b.com",
                    name="Alguém",
                    path="/caminho/que/nao/existe.txt",
                )

    def test_template_com_variavel_invalida_levanta_key_error(self, tmp_path):
        from src.services.sendMail import buildMail

        template_invalido = tmp_path / "invalido.txt"
        template_invalido.write_text("Olá {variavel_inexistente}.", encoding="utf-8")

        with patch("src.services.sendMail.settings", _criar_mock_settings()):
            with pytest.raises(KeyError):
                buildMail(
                    to="a@b.com",
                    name="Alguém",
                    path=str(template_invalido),
                )


class TestSendMail:
    def test_envia_mensagem_com_sucesso(self, arquivo_template):
        from src.services.sendMail import sendMail

        mock_settings = _criar_mock_settings(arquivo_template)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.settings", mock_settings), \
             patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            sendMail(to="destino@teste.com", name="Usuário")

        mock_smtp.send_message.assert_called_once()

    def test_smtp_connect_error_levanta_http_500(self, arquivo_template):
        from src.services.sendMail import sendMail

        mock_settings = _criar_mock_settings(arquivo_template)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(side_effect=SMTPConnectError(421, b"falha"))
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.settings", mock_settings), \
             patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            with pytest.raises(HTTPException) as exc_info:
                sendMail(to="destino@teste.com", name="Usuário")

        assert exc_info.value.status_code == 500
        assert "SMTP" in exc_info.value.detail

    def test_smtp_auth_error_levanta_http_500(self, arquivo_template):
        from src.services.sendMail import sendMail

        mock_settings = _criar_mock_settings(arquivo_template)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(
            side_effect=SMTPAuthenticationError(535, b"credenciais invalidas")
        )
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.settings", mock_settings), \
             patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            with pytest.raises(HTTPException) as exc_info:
                sendMail(to="destino@teste.com", name="Usuário")

        assert exc_info.value.status_code == 500
        assert "autenticação" in exc_info.value.detail.lower() or "smtp" in exc_info.value.detail.lower()

    def test_template_com_variavel_invalida_levanta_key_error(self, tmp_path):
        # buildMail é chamado ANTES do bloco try/except do SMTP em sendMail,
        # portanto o KeyError de template inválido propaga sem ser convertido em HTTPException.
        from src.services.sendMail import sendMail

        template_invalido = tmp_path / "invalido.txt"
        template_invalido.write_text("Olá {variavel_inexistente}.", encoding="utf-8")

        mock_settings = _criar_mock_settings(str(template_invalido))

        with patch("src.services.sendMail.settings", mock_settings):
            with pytest.raises(KeyError):
                sendMail(to="destino@teste.com", name="Usuário")

    def test_path_validator_e_chamado(self, arquivo_template):
        from src.services.sendMail import sendMail

        mock_settings = _criar_mock_settings(arquivo_template)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("src.services.sendMail.settings", mock_settings), \
             patch("src.services.sendMail.SMTP_SSL", return_value=mock_smtp):
            sendMail(to="destino@teste.com", name="Usuário")

        mock_settings.path_validator.assert_called_once()
