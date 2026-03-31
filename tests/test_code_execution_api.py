from fastapi.testclient import TestClient

from progressive_exposure.code_execution_api.app import app
from progressive_exposure.code_execution_api.js_script_runner import MAX_CODE_SIZE

client = TestClient(app)


class TestCodeExecutionAPI:
    def test_simple_console_log(self) -> None:
        resp = client.post("/api/v1/execute", json={"code": 'console.log("hello")'})
        assert resp.status_code == 200
        body = resp.json()
        assert body["output"] == "hello"
        assert body["exit_code"] == 0
        assert body["timed_out"] is False

    def test_computation(self) -> None:
        resp = client.post("/api/v1/execute", json={"code": "console.log(2 + 2)"})
        assert resp.status_code == 200
        assert resp.json()["output"] == "4"

    def test_empty_code_returns_400(self) -> None:
        resp = client.post("/api/v1/execute", json={"code": ""})
        assert resp.status_code == 400
        assert "No code provided" in resp.json()["detail"]

    def test_whitespace_code_returns_400(self) -> None:
        resp = client.post("/api/v1/execute", json={"code": "   \n  "})
        assert resp.status_code == 400
        assert "No code provided" in resp.json()["detail"]

    def test_code_too_large_returns_400(self) -> None:
        code = "// x\n" * (MAX_CODE_SIZE + 1)
        resp = client.post("/api/v1/execute", json={"code": code})
        assert resp.status_code == 400
        assert "exceeds maximum size" in resp.json()["detail"]

    def test_runtime_error(self) -> None:
        resp = client.post(
            "/api/v1/execute", json={"code": 'throw new Error("boom");'}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "boom" in body["output"]
        assert body["exit_code"] != 0
        assert body["timed_out"] is False

    def test_syntax_error(self) -> None:
        resp = client.post("/api/v1/execute", json={"code": "function foo("})
        assert resp.status_code == 200
        body = resp.json()
        assert body["exit_code"] != 0

    def test_missing_code_field(self) -> None:
        resp = client.post("/api/v1/execute", json={})
        assert resp.status_code == 422  # Pydantic validation error

    def test_arrow_function_and_template_literal(self) -> None:
        code = 'const greet = (n) => `Hello, ${n}!`;\nconsole.log(greet("JS"));'
        resp = client.post("/api/v1/execute", json={"code": code})
        assert resp.status_code == 200
        assert resp.json()["output"] == "Hello, JS!"
