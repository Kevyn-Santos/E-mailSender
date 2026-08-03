from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from Main import app
from src.core.security import Rate_limiter
from src.core.settings import settings

client = TestClient(app)


# Cada teste começa com a contagem do rate limiter zerada, senão os testes
# poluiriam a contagem uns dos outros (mesmo client IP no TestClient).
@pytest.fixture(autouse=True)
def resetar_rate_limiter():
    Rate_limiter.limiter.reset()
    yield
    Rate_limiter.limiter.reset()


class TestSendMailEndpoint:
    def test_payload_valido_retorna_200(self):
        with patch("src.routes.Sender.sendMail"):
            resposta = client.post(
                "/sendMail",
                json={"userMail": "destino@teste.com", "userName": "Usuário Teste"},
            )
        assert resposta.status_code == 200

    def test_dispara_sendmail_com_dados_sanitizados(self):
        with patch("src.routes.Sender.sendMail") as mock_send:
            client.post(
                "/sendMail",
                json={"userMail": "destino@teste.com", "userName": "Usuário123 Teste!"},
            )
        mock_send.assert_called_once()
        chamada = mock_send.call_args.kwargs
        assert chamada["to"] == "destino@teste.com"
        assert chamada["name"] == "Usuário Teste"
        assert chamada["config"].sender == settings.SENDER

    def test_config_do_request_sobrepoe_env(self):
        with patch("src.routes.Sender.sendMail") as mock_send:
            client.post(
                "/sendMail",
                json={
                    "userMail": "destino@teste.com",
                    "userName": "Usuário",
                    "config": {
                        "sender": "outro@teste.com",
                        "password": "outra-senha",
                        "subject": "Assunto customizado",
                        "template": "Olá {usuario}!",
                    },
                },
            )
        chamada = mock_send.call_args.kwargs
        assert chamada["config"].sender == "outro@teste.com"
        assert chamada["config"].subject == "Assunto customizado"
        assert chamada["config"].template == "Olá {usuario}!"

    def test_sem_sender_e_password_em_lugar_nenhum_retorna_422(self):
        with (
            patch("src.core.mail_config.settings.SENDER", None),
            patch("src.core.mail_config.settings.PASS", None),
        ):
            resposta = client.post(
                "/sendMail",
                json={"userMail": "destino@teste.com", "userName": "Usuário"},
            )
        assert resposta.status_code == 422

    def test_email_invalido_retorna_422(self):
        resposta = client.post(
            "/sendMail",
            json={"userMail": "nao-e-email", "userName": "Usuário"},
        )
        assert resposta.status_code == 422

    def test_campo_faltando_retorna_422(self):
        resposta = client.post("/sendMail", json={"userMail": "a@b.com"})
        assert resposta.status_code == 422

    def test_estouro_de_rate_limit_retorna_429(self):
        with patch("src.routes.Sender.sendMail"):
            for _ in range(settings.QTD_EMAILS):
                resposta = client.post(
                    "/sendMail",
                    json={"userMail": "destino@teste.com", "userName": "Usuário"},
                )
                assert resposta.status_code == 200

            resposta_excedente = client.post(
                "/sendMail",
                json={"userMail": "destino@teste.com", "userName": "Usuário"},
            )

        assert resposta_excedente.status_code == 429
        assert resposta_excedente.json()["error"] == "Muitas requisições"
