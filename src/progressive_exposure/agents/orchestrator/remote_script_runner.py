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
    url = f"{base_url}/execute"

    payload = json.dumps({"code": code}).encode("utf-8")

    print(f"--- Remote execution request ---", flush=True)
    print(f"POST {url}", flush=True)
    print(f"Content-Type: application/json", flush=True)
    print(f"Payload:\n{payload.decode('utf-8')}", flush=True)
    print(f"--- End request ---", flush=True)

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw_response = resp.read().decode("utf-8")
            print(f"--- Remote execution response (HTTP {resp.status}) ---", flush=True)
            print(raw_response, flush=True)
            print(f"--- End response ---", flush=True)
            body = json.loads(raw_response)
            result = body.get("result", body.get("output"))
            if result is None:
                return "(no output)"
            return result if isinstance(result, str) else json.dumps(result)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"--- Remote execution error (HTTP {e.code}) ---", flush=True)
        print(error_body, flush=True)
        print(f"--- End error ---", flush=True)
        try:
            detail = json.loads(error_body).get("detail", e.reason)
        except Exception:
            detail = e.reason
        return f"Error: Remote execution failed (HTTP {e.code}): {detail}"
    except urllib.error.URLError as e:
        return f"Error: Could not reach remote execution service at {url} — {e.reason}"
    except TimeoutError:
        return f"Error: Remote execution request timed out after {REQUEST_TIMEOUT} seconds."
