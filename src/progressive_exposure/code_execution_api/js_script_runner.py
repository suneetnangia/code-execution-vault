# Copyright (c) Microsoft. All rights reserved.

"""JavaScript script runner for dynamically generated code.

Executes JavaScript code in an isolated Node.js subprocess via a temporary file.
This is provided as a PoC stand-in for a remote execution service.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_CODE_SIZE = 10_240  # 10 KB
EXECUTION_TIMEOUT = 60  # seconds
MAX_OUTPUT_SIZE = 50_000  # characters


def _find_node() -> str:
    """Return the absolute path to the Node.js executable."""
    node = shutil.which("node")
    if node is None:
        raise FileNotFoundError("Node.js ('node') is not installed or not on PATH.")
    return node


def js_script_runner(code: str) -> tuple[str, int, bool]:
    """Run dynamically generated JavaScript code in a Node.js subprocess.

    Writes the code to a temporary file, executes it with Node.js,
    and returns captured output.

    Args:
        code: The JavaScript source code to execute.

    Returns:
        A tuple of (output, exit_code, timed_out).
    """
    if not code or not code.strip():
        return ("Error: No code provided.", 1, False)

    if len(code) > MAX_CODE_SIZE:
        return (f"Error: Code exceeds maximum size of {MAX_CODE_SIZE} bytes.", 1, False)

    node_path = _find_node()
    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            prefix="exec_",
            delete=False,
        )
        tmp_file.write(code)
        tmp_file.close()

        # Run with minimal environment to avoid leaking secrets
        safe_env = {
            "PATH": "/usr/bin:/bin",
            "HOME": tempfile.gettempdir(),
            "NODE_PATH": "",
            "NODE_OPTIONS": "",
            "LC_ALL": "C.UTF-8",
        }

        result = subprocess.run(
            [node_path, tmp_file.name],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            cwd=tempfile.gettempdir(),
            env=safe_env,
        )

        output = result.stdout
        if result.stderr:
            output += f"\nStderr:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nScript exited with code {result.returncode}"

        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

        return (output.strip() or "(no output)", result.returncode, False)

    except subprocess.TimeoutExpired:
        return (
            f"Error: Code execution timed out after {EXECUTION_TIMEOUT} seconds.",
            1,
            True,
        )
    except OSError as e:
        return (f"Error: Failed to execute code: {e}", 1, False)
    finally:
        if tmp_file is not None:
            Path(tmp_file.name).unlink(missing_ok=True)
