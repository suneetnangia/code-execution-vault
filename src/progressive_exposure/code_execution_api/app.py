import uvicorn
from fastapi import FastAPI

from .router import router

app = FastAPI(
    title="Code Execution API",
    description="PoC API for remote JavaScript code execution via Node.js.",
    version="1.0.0",
)

app.include_router(router)


def main() -> None:
    uvicorn.run(
        "progressive_exposure.code_execution_api.app:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
    )


if __name__ == "__main__":
    main()
