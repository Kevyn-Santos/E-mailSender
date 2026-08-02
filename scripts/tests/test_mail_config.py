from unittest.mock import patch

import pytest
from fastapi import HTTPException

from src.core.mail_config import ResolvedMailConfig, resolve_mail_config
from src.models.emailModules import MailConfig


class TestResolveMailConfig:
    def test_sem_request_config_usa_tudo_do_env(self):
        resultado = resolve_mail_config(None)
        assert isinstance(resultado, ResolvedMailConfig)
        assert resultado.sender is not None
        assert resultado.password is not None

    def test_request_sobrepoe_env_campo_a_campo(self):
        config = MailConfig(sender="dev@exemplo.com", subject="Assunto do dev")
        resultado = resolve_mail_config(config)

        assert resultado.sender == "dev@exemplo.com"
        assert resultado.subject == "Assunto do dev"
        # password não foi informado no request, deve cair pro ENV
        with patch("src.core.mail_config.settings.PASS", "senha-do-env"):
            resultado_com_env = resolve_mail_config(config)
        assert resultado_com_env.password == "senha-do-env"

    def test_template_inline_do_request_e_usado(self):
        config = MailConfig(template="Olá {usuario}, teste.")
        resultado = resolve_mail_config(config)
        assert resultado.template == "Olá {usuario}, teste."

    def test_template_ausente_usa_default_do_arquivo(self):
        resultado = resolve_mail_config(None)
        assert "{usuario}" in resultado.template

    def test_sender_ausente_em_todos_niveis_levanta_422(self):
        with patch("src.core.mail_config.settings.SENDER", None):
            config = MailConfig(sender=None)
            with pytest.raises(HTTPException) as exc_info:
                resolve_mail_config(config)
        assert exc_info.value.status_code == 422

    def test_password_ausente_em_todos_niveis_levanta_422(self):
        with patch("src.core.mail_config.settings.PASS", None):
            config = MailConfig(password=None)
            with pytest.raises(HTTPException) as exc_info:
                resolve_mail_config(config)
        assert exc_info.value.status_code == 422

    def test_porta_smtp_zero_no_request_nao_cai_pro_env(self):
        # 0 é um valor explícito (não None), então deve ser respeitado mesmo sendo falsy.
        config = MailConfig(port_smtp=0)
        resultado = resolve_mail_config(config)
        assert resultado.port_smtp == 0
