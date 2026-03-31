from progressive_exposure.code_execution_api.js_script_runner import (
    MAX_CODE_SIZE,
    js_script_runner,
)


class TestJsScriptRunner:
    def test_simple_console_log(self) -> None:
        output, exit_code, timed_out = js_script_runner('console.log("hello")')
        assert output == "hello"
        assert exit_code == 0
        assert timed_out is False

    def test_computation(self) -> None:
        output, exit_code, _ = js_script_runner("console.log(2 + 2)")
        assert output == "4"
        assert exit_code == 0

    def test_multiline_code(self) -> None:
        code = "const x = 3;\nconst y = 7;\nconsole.log(x * y);"
        output, exit_code, _ = js_script_runner(code)
        assert output == "21"
        assert exit_code == 0

    def test_arrow_function(self) -> None:
        code = "const add = (a, b) => a + b;\nconsole.log(add(10, 32));"
        output, exit_code, _ = js_script_runner(code)
        assert output == "42"
        assert exit_code == 0

    def test_template_literal(self) -> None:
        code = 'const name = "world";\nconsole.log(`hello ${name}`);'
        output, exit_code, _ = js_script_runner(code)
        assert output == "hello world"
        assert exit_code == 0

    def test_json_processing(self) -> None:
        code = 'const data = JSON.parse(\'{"a":1,"b":2}\');\nconsole.log(data.a + data.b);'
        output, exit_code, _ = js_script_runner(code)
        assert output == "3"
        assert exit_code == 0

    def test_empty_code(self) -> None:
        output, exit_code, timed_out = js_script_runner("")
        assert "No code provided" in output
        assert exit_code == 1
        assert timed_out is False

    def test_whitespace_only_code(self) -> None:
        output, exit_code, _ = js_script_runner("   \n  ")
        assert "No code provided" in output

    def test_code_exceeds_max_size(self) -> None:
        code = "// padding\n" * (MAX_CODE_SIZE + 1)
        output, exit_code, _ = js_script_runner(code)
        assert "exceeds maximum size" in output
        assert exit_code == 1

    def test_syntax_error(self) -> None:
        output, exit_code, _ = js_script_runner("function foo(")
        assert "Stderr:" in output or "SyntaxError" in output
        assert exit_code != 0

    def test_runtime_error(self) -> None:
        output, exit_code, _ = js_script_runner('throw new Error("test error");')
        assert "test error" in output
        assert exit_code != 0

    def test_no_output(self) -> None:
        output, exit_code, _ = js_script_runner("const x = 42;")
        assert output == "(no output)"
        assert exit_code == 0

    def test_temp_file_cleaned_up(self) -> None:
        import glob
        import tempfile

        before = set(glob.glob(f"{tempfile.gettempdir()}/exec_*.js"))
        js_script_runner('console.log("cleanup test")')
        after = set(glob.glob(f"{tempfile.gettempdir()}/exec_*.js"))
        assert after == before, "Temp file was not cleaned up"
