from pydantic import BaseModel


class CodeExecutionRequest(BaseModel):
    code: str


class CodeExecutionResponse(BaseModel):
    output: str
    exit_code: int
    timed_out: bool
