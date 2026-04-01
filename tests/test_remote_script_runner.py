import json
import os
import urllib.error
from http.client import HTTPResponse
from io import BytesIO
from unittest.mock import patch, MagicMock

from progressive_exposure.agents.orchestrator.remote_script_runner import (
    remote_script_runner,
    DEFAULT_API_URL,
)


def _mock_response(body: dict, status: int = 200) -> MagicMock:
    """Create a mock urllib response with the given JSON body."""
    data = json.dumps(body).encode("utf-8")
    mock = MagicMock()
    mock.read.return_value = data
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


class TestRemoteScriptRunner:
    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_successful_execution(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {"output": "hello", "exit_code": 0, "timed_out": False}
        )
        result = remote_script_runner('console.log("hello")')
        assert result == "hello"

        # Verify the request was made correctly
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.full_url == f"{DEFAULT_API_URL}/execute"
        assert req.method == "POST"
        assert json.loads(req.data) == {"code": 'console.log("hello")'}

    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_no_output_field(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"exit_code": 0, "timed_out": False})
        result = remote_script_runner("const x = 1;")
        assert result == "(no output)"

    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_http_error_with_detail(self, mock_urlopen: MagicMock) -> None:
        error_body = json.dumps({"detail": "No code provided."}).encode("utf-8")
        http_error = urllib.error.HTTPError(
            url=f"{DEFAULT_API_URL}/execute",
            code=400,
            msg="Bad Request",
            hdrs=None,  # type: ignore[arg-type]
            fp=BytesIO(error_body),
        )
        mock_urlopen.side_effect = http_error
        result = remote_script_runner("")
        assert "HTTP 400" in result
        assert "No code provided" in result

    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_connection_refused(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = urllib.error.URLError(
            reason=ConnectionRefusedError("Connection refused")
        )
        result = remote_script_runner('console.log("test")')
        assert "Could not reach remote execution service" in result

    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_timeout(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = TimeoutError()
        result = remote_script_runner('console.log("test")')
        assert "timed out" in result

    @patch.dict(os.environ, {"REMOTE_CODE_EXECUTION_URL": "http://custom-host:9999"})
    @patch("progressive_exposure.agents.orchestrator.remote_script_runner.urllib.request.urlopen")
    def test_custom_url_from_env(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {"output": "ok", "exit_code": 0, "timed_out": False}
        )
        result = remote_script_runner('console.log("ok")')
        assert result == "ok"

        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://custom-host:9999/execute"
