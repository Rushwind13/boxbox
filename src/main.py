# src/main.py
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging
import uvicorn
import sys
import traceback
import uuid

# --- Logging setup (JSON, rotation-ready, production-hardened) ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        record_dict = record.__dict__.copy()
        return str({
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace": record_dict.get("exc_text") or ""
        })

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
for handler in logging.getLogger().handlers:
    handler.setFormatter(JsonFormatter())
logger = logging.getLogger("api")

# --- FastAPI app ---
app = FastAPI(
    title="Sample FastAPI RESTful API",
    description="API that processes POSTed JSON, health/version checks, with OpenAPI docs.",
    version="0.1.0"
)

# --- CORS Middleware (production: restrict origins) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # response.headers["Content-Security-Policy"] = "default-src 'self';" # Uncomment to enable CSP
        return response
app.add_middleware(SecurityHeadersMiddleware)

# --- Placeholder Request/Response schemas ---
class RequestSchema(BaseModel):
    # TODO: Define your actual fields here
    input_data: str

class ResponseSchema(BaseModel):
    # TODO: Define your actual fields here
    result: str

class ErrorResponse(BaseModel):
    error: str
    code: int
    request_id: str = ""

# --- Global error handlers ---

# Handles FastAPI validation errors (missing fields, bad JSON, etc)
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def fastapi_request_validation_exception_handler(request: Request, exc):
    request_id = str(uuid.uuid4())
    logger.warning(f"FastAPI request validation error: {exc} | request_id={request_id}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation failed: " + str(exc.errors()),
            code=422,
            request_id=request_id
        ).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    tb = traceback.format_exc()
    logger.error(f"Unhandled error: {exc} | request_id={request_id}\n{tb}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error.",
            code=500,
            request_id=request_id
        ).model_dump()
    )

# --- POST endpoint (/process) ---
@app.post("/process", response_model=ResponseSchema, responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def process(request: RequestSchema):
    logger.info(f"Received request: {request.model_dump_json()}")
    # TODO: Core logic goes here
    output = f"Echo: {request.input_data}"
    return ResponseSchema(result=output)

# --- GET endpoint (/health) ---
@app.get("/health")
async def health():
    # Expand with deeper checks as infra grows
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})

# --- GET endpoint (/version) ---
@app.get("/version")
async def version():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"version": app.version})

# --- Uvicorn entrypoint for local dev/run ---
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
