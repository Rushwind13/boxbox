# main.py
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import uvicorn

# --- Logging setup (structured, rotation-ready) ---
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
        # Extend: add RotatingFileHandler or CloudWatch for prod as needed
    ]
)
logger = logging.getLogger("api")

# --- FastAPI app ---
app = FastAPI(
    title="Sample FastAPI RESTful API",
    description="API that processes POSTed JSON, health/version checks, with OpenAPI docs.",
    version="0.1.0"
)

# --- Placeholder Request/Response schemas ---
class RequestSchema(BaseModel):
    # TODO: Define your actual fields here
    input_data: str

class ResponseSchema(BaseModel):
    # TODO: Define your actual fields here
    result: str

# --- POST endpoint (/process) ---
@app.post("/process", response_model=ResponseSchema)
async def process(request: RequestSchema):
    logger.info(f"Received request: {request.json()}")
    # TODO: Core logic goes here
    output = f"Echo: {request.input_data}"
    return ResponseSchema(result=output)

# --- GET endpoint (/health) ---
@app.get("/health")
async def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})

# --- GET endpoint (/version) ---
@app.get("/version")
async def version():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"version": app.version})

# --- Uvicorn entrypoint for local dev/run ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)