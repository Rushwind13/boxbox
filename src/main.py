import os
from fastapi import FastAPI, Request, Response, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging
import uvicorn
import sys
import traceback
import uuid
import jwt
from datetime import datetime, timedelta

# === Rate limiting ===
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# === ENVIRONMENT ===
ENV = os.getenv("ENV", "prod")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://yourdomain.com").split(",")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# --- Logging setup (unchanged, omitted for brevity — use prior block) ---

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

# --- App definition ---
app = FastAPI(
    title="Secure FastAPI RESTful API",
    description="Hardened API with JWT auth, CORS lockdown, docs hidden in production, and rate limiting.",
    version="0.1.0",
    docs_url="/docs" if ENV == "dev" else None,
    redoc_url="/redoc" if ENV == "dev" else None,
    openapi_url="/openapi.json" if ENV == "dev" else None
)

# === Rate limiter (SlowAPI) setup ===
limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    request_id = str(uuid.uuid4())
    logger.warning(f"Rate limit exceeded: {exc} | request_id={request_id}")
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error="Rate limit exceeded. Please try again later.",
            code=429,
            request_id=request_id
        ).model_dump()
    )

# --- CORS & Security headers setup (unchanged, see previous block) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ENV == "prod" else ["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
app.add_middleware(SecurityHeadersMiddleware)

# --- JWT Auth code (unchanged, see previous block) ---
security = HTTPBearer(auto_error=False)
def create_jwt(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Schemas & Error handlers (unchanged, see previous block) ---
class RequestSchema(BaseModel):
    input_data: str
class ResponseSchema(BaseModel):
    result: str
class ErrorResponse(BaseModel):
    error: str
    code: int
    request_id: str = ""
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

# --- Token endpoint (for demo) ---
@app.post("/token")
async def get_token():
    demo_user_id = "demo-user"
    token = create_jwt(demo_user_id)
    return {"access_token": token, "token_type": "bearer"}

# --- Protected POST endpoint (/process) WITH RATE LIMITING ---
@app.post("/process", response_model=ResponseSchema, responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
@limiter.limit("5/minute")  # Custom rate limit for this endpoint: 5 reqs per minute per IP
async def process(request: Request, payload: RequestSchema, user_id: str = Depends(verify_jwt)):
    logger.info(f"Received request from {user_id}: {payload.model_dump_json()}")
    output = f"Echo: {payload.input_data}"
    return ResponseSchema(result=output)

# --- Health endpoint (unprotected, but rate-limited globally) ---
@app.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})

# --- Version endpoint (unprotected) ---
@app.get("/version")
async def version():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"version": app.version})

# --- Uvicorn entrypoint ---
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=(ENV == "dev"))
