from fastapi.testclient import TestClient

from progressive_exposure.code_execution_api.app import app
from progressive_exposure.code_execution_api.router import MAX_CODE_SIZE

client = TestClient(app)


class TestCodeExecutionAPI:
    def test_valid_code_returns_stub_response(self) -> None:
        resp = client.post("/execute", json={"code": 'console.log("hello")'})
        assert resp.status_code == 200
        body = resp.json()
        assert body["output"] == "Code received and logged successfully."
        assert body["exit_code"] == 0
        assert body["timed_out"] is False

    def test_multiline_code_accepted(self) -> None:
        code = "const x = 1;\nconst y = 2;\nconsole.log(x + y);"
        resp = client.post("/execute", json={"code": code})
        assert resp.status_code == 200
        assert resp.json()["exit_code"] == 0

    def test_empty_code_returns_400(self) -> None:
        resp = client.post("/execute", json={"code": ""})
        assert resp.status_code == 400
        assert "No code provided" in resp.json()["detail"]

    def test_whitespace_code_returns_400(self) -> None:
        resp = client.post("/execute", json={"code": "   \n  "})
        assert resp.status_code == 400
        assert "No code provided" in resp.json()["detail"]

    def test_code_too_large_returns_400(self) -> None:
        code = "// x\n" * (MAX_CODE_SIZE + 1)
        resp = client.post("/execute", json={"code": code})
        assert resp.status_code == 400
        assert "exceeds maximum size" in resp.json()["detail"]

    def test_missing_code_field(self) -> None:
        resp = client.post("/execute", json={})
        assert resp.status_code == 422  # Pydantic validation error
