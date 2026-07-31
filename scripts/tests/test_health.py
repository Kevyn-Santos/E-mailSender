from fastapi.testclient import TestClient

from Main import app

client = TestClient(app)


class TestHealthCheck:
    def test_retorna_200(self):
        resposta = client.get("/health")
        assert resposta.status_code == 200

    def test_corpo_correto(self):
        resposta = client.get("/health")
        assert resposta.json() == {"Status": 200, "Description": "OK"}
