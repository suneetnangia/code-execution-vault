#!/usr/bin/env python3
"""Send JavaScript code to a remote execution service and return the output.

Usage:
    python run_js.py --code <JAVASCRIPT_CODE>

Sends the JavaScript code as a JSON payload to the remote execution API
and returns the execution result.
Uses only Python standard library modules.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

# TODO: Update this URL once the remote JavaScript execution API is built.
API_URL = "http://localhost:3000/api/execute"

REQUEST_TIMEOUT = 30  # seconds


def execute_js(code: str) -> str:
    """Send JavaScript code to the remote execution API and return the output.

    Args:
        code: The JavaScript source code to execute.

    Returns:
        The execution output as a string, or an error message.
    """
    if not code or not code.strip():
        return "Error: No code provided."

    payload = json.dumps({"code": code}).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            result = resp.read().decode("utf-8")
            return result
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        return f"Error: HTTP {e.code} from execution service.\n{body}".strip()
    except urllib.error.URLError as e:
        return f"Error: Could not reach execution service at {API_URL}: {e.reason}"
    except TimeoutError:
        return f"Error: Request to execution service timed out after {REQUEST_TIMEOUT} seconds."


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute JavaScript code via a remote execution service."
    )
    parser.add_argument(
        "--code",
        required=True,
        help="The JavaScript source code to execute.",
    )
    args = parser.parse_args()

    result = execute_js(args.code)
    print(result)


if __name__ == "__main__":
    main()
