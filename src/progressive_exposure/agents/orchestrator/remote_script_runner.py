# Copyright (c) Microsoft. All rights reserved.

"""Remote code execution client.

Sends code to a remote execution API and returns the output.
The API endpoint is configurable via the REMOTE_CODE_EXECUTION_URL
environment variable, defaulting to http://localhost:8100.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_API_URL = "http://localhost:8100"
REQUEST_TIMEOUT = 90  # seconds — generous to allow for remote execution time


def remote_script_runner(code: str) -> str:
    """Send code to a remote execution API and return the output.

    Args:
        code: The JavaScript source code to execute remotely.

    Returns:
        The execution output, or an error message.
    """
    base_url = os.environ.get("REMOTE_CODE_EXECUTION_URL", DEFAULT_API_URL)
    url = f"{base_url}/api/v1/execute"

    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("output", "(no output)")
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8")).get("detail", e.reason)
        except Exception:
            detail = e.reason
        return f"Error: Remote execution failed (HTTP {e.code}): {detail}"
    except urllib.error.URLError as e:
        return f"Error: Could not reach remote execution service at {url} — {e.reason}"
    except TimeoutError:
        return f"Error: Remote execution request timed out after {REQUEST_TIMEOUT} seconds."
