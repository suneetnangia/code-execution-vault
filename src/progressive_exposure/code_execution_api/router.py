from fastapi import APIRouter, HTTPException

from .js_script_runner import MAX_CODE_SIZE, js_script_runner
from .models import CodeExecutionRequest, CodeExecutionResponse

router = APIRouter(prefix="/api/v1", tags=["Code Execution"])


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

    output, exit_code, timed_out = js_script_runner(code)

    return CodeExecutionResponse(
        output=output,
        exit_code=exit_code,
        timed_out=timed_out,
    )
