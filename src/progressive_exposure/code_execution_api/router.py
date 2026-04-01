import logging

from fastapi import APIRouter, HTTPException

from .models import CodeExecutionRequest, CodeExecutionResponse

logger = logging.getLogger(__name__)

MAX_CODE_SIZE = 10_240  # 10 KB

router = APIRouter(tags=["Code Execution"])


@router.post("/execute", response_model=CodeExecutionResponse)
def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    """Accept JavaScript code, log it, and return a stub response."""
    code = request.code

    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="No code provided.")

    if len(code) > MAX_CODE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Code exceeds maximum size of {MAX_CODE_SIZE} bytes.",
        )

    logger.info("--- Received JavaScript code ---\n%s\n--- End of code ---", code)
    print(f"--- Received JavaScript code ---\n{code}\n--- End of code ---", flush=True)

    return CodeExecutionResponse(
        output="Code received and logged successfully.",
        exit_code=0,
        timed_out=False,
    )
