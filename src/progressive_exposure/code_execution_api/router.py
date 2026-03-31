import logging

from fastapi import APIRouter, HTTPException

from .js_script_runner import MAX_CODE_SIZE, js_script_runner
from .models import CodeExecutionRequest, CodeExecutionResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Code Execution"])


@router.post("/execute", response_model=CodeExecutionResponse)
def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    """Execute JavaScript code in an isolated Node.js subprocess."""
    code = request.code

    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="No code provided.")

    if len(code) > MAX_CODE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Code exceeds maximum size of {MAX_CODE_SIZE} bytes.",
        )

    logger.info("--- Received JavaScript code ---\n%s\n--- End of code ---", code)

    output, exit_code, timed_out = js_script_runner(code)

    return CodeExecutionResponse(
        output=output,
        exit_code=exit_code,
        timed_out=timed_out,
    )
