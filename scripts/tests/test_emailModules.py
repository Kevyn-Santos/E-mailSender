import pytest
from pydantic import ValidationError
from src.models.emailModules import baseUser


class TestBaseUserValidacao:
    def test_modelo_valido(self):
        usuario = baseUser(userMail="joao@exemplo.com", userName="João Silva")
        assert usuario.userMail == "joao@exemplo.com"
        assert usuario.userName == "João Silva"

    def test_email_invalido_levanta_validation_error(self):
        with pytest.raises(ValidationError):
            baseUser(userMail="isso-nao-e-email", userName="João")

    def test_email_sem_dominio_levanta_validation_error(self):
        with pytest.raises(ValidationError):
            baseUser(userMail="joao@", userName="João")

    def test_username_aceita_string_qualquer(self):
        usuario = baseUser(userMail="a@b.com", userName="123!@#")
        assert usuario.userName == "123!@#"


class TestSanitizeName:
    def _sanitizar(self, nome: str) -> str:
        return baseUser(userMail="a@b.com", userName=nome).SanitizeName()

    def test_nome_limpo_retorna_igual(self):
        assert self._sanitizar("Maria") == "Maria"

    def test_nome_com_acentos_preservados(self):
        assert self._sanitizar("José Ângela") == "José Ângela"

    def test_numeros_sao_removidos(self):
        assert self._sanitizar("João123") == "João"

    def test_caracteres_especiais_sao_removidos(self):
        assert self._sanitizar("Ana!@#$%") == "Ana"

    def test_espacos_multiplos_sao_normalizados(self):
        assert self._sanitizar("  Carlos   Eduardo  ") == "Carlos Eduardo"

    def test_nome_so_com_caracteres_invalidos_retorna_vazio(self):
        assert self._sanitizar("123!@#") == ""

    def test_nome_com_hifen_remove_hifen(self):
        # hífen não é letra, deve ser removido
        assert self._sanitizar("Ana-Paula") == "Ana Paula"

    def test_nome_completo_com_sobrenome(self):
        assert self._sanitizar("Kevyn Santos") == "Kevyn Santos"
