import json
from unittest.mock import ANY, MagicMock, patch

from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.security import Rate_limiter


class TestLimiterConfig:
    def test_key_func_e_get_remote_address(self):
        assert Rate_limiter.limiter._key_func is get_remote_address

    def test_estrategia_e_moving_window(self):
        assert Rate_limiter.limiter._strategy == "moving-window"

    def test_storage_uri_vem_das_settings(self):
        from src.core.settings import settings

        assert Rate_limiter.limiter._storage_uri == settings.RATE_LIMIT_STORAGE_URI


class TestGetRateLimitString:
    def test_formato_qtd_por_tmp_seconds(self):
        mock_settings = MagicMock(QTD_EMAILS=5, TMP_EMAILS=30)

        with patch("src.core.security.settings", mock_settings):
            resultado = Rate_limiter.get_rate_limit_string()

        assert resultado == "5/30 seconds"

    def test_usa_valores_atuais_das_settings(self):
        mock_settings = MagicMock(QTD_EMAILS=1, TMP_EMAILS=1)

        with patch("src.core.security.settings", mock_settings):
            resultado = Rate_limiter.get_rate_limit_string()

        assert resultado == "1/1 seconds"


class TestRateLimitExceededHandler:
    def _criar_mock_request(self):
        mock_request = MagicMock()
        mock_request.state.view_rate_limit = "estado-do-limite"
        mock_request.app.state.limiter._inject_headers = MagicMock(
            side_effect=lambda response, view_rate_limit: response
        )
        return mock_request

    def test_retorna_json_response_429(self):
        mock_request = self._criar_mock_request()
        mock_exc = MagicMock(spec=RateLimitExceeded)

        resposta = Rate_limiter.rate_limit_exceeded_handler(mock_request, mock_exc)

        assert isinstance(resposta, JSONResponse)
        assert resposta.status_code == 429

    def test_corpo_contem_error_e_detail(self):
        mock_request = self._criar_mock_request()
        mock_exc = MagicMock(spec=RateLimitExceeded)

        resposta = Rate_limiter.rate_limit_exceeded_handler(mock_request, mock_exc)
        corpo = json.loads(resposta.body)

        assert corpo["error"] == "Muitas requisições"
        assert "detail" in corpo

    def test_injeta_headers_de_rate_limit(self):
        mock_request = self._criar_mock_request()
        mock_exc = MagicMock(spec=RateLimitExceeded)

        Rate_limiter.rate_limit_exceeded_handler(mock_request, mock_exc)

        mock_request.app.state.limiter._inject_headers.assert_called_once_with(
            ANY, "estado-do-limite"
        )
