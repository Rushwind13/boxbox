import logging
import os
import sys
import traceback
import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

ENV = os.getenv("ENV", "prod")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://yourdomain.com").split(",")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60


class JsonFormatter(logging.Formatter):

    def format(self, record):
        record_dict = record.__dict__.copy()
        return str(
            {
                "time": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "trace": record_dict.get("exc_text") or "",
            }
        )


logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(JsonFormatter())

logger = logging.getLogger("api")

app = FastAPI(
    title="Secure FastAPI RESTful API",
    description="Versioned API with JWT, rate limiting, CORS lockdown, and hidden docs in prod.",
    version="1.0.0",
    docs_url="/docs" if ENV == "dev" else None,
    redoc_url="/redoc" if ENV == "dev" else None,
    openapi_url="/openapi.json" if ENV == "dev" else None,
)

limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    request_id = str(uuid.uuid4())
    logger.warning(f"Rate limit exceeded: {exc} | request_id={request_id}")
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error="Rate limit exceeded. Please try again later.", code=429, request_id=request_id
        ).model_dump(),
    )


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
            error="Validation failed: " + str(exc.errors()), code=422, request_id=request_id
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    tb = traceback.format_exc()
    logger.error(f"Unhandled error: {exc} | request_id={request_id}\n{tb}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error.", code=500, request_id=request_id
        ).model_dump(),
    )


v1_router = APIRouter(prefix="/v1", tags=["v1"])


@v1_router.post("/token")
async def get_token_v1():
    demo_user_id = "demo-user"
    token = create_jwt(demo_user_id)
    return {"access_token": token, "token_type": "bearer"}


@v1_router.post(
    "/process",
    response_model=ResponseSchema,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    },
)
@limiter.limit("5/minute")
async def process_v1(request: Request, payload: RequestSchema, user_id: str = Depends(verify_jwt)):
    logger.info(f"Received v1 request from {user_id}: {payload.model_dump_json()}")
    output = f"Echo: {payload.input_data}"
    return ResponseSchema(result=output)


@v1_router.get("/health")
@limiter.limit("30/minute")
async def health_v1(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@v1_router.get("/version")
async def version_v1():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"version": app.version, "api_version": "v1"}
    )


v2_router = APIRouter(prefix="/v2", tags=["v2"])


@v2_router.post("/process")
async def process_v2(request: Request, payload: RequestSchema, user_id: str = Depends(verify_jwt)):
    logger.info(f"Received v2 request from {user_id}: {payload.model_dump_json()}")
    output = f"V2: You sent {payload.input_data.upper()}"
    return {"result": output, "api_version": "v2"}


@v2_router.get("/health")
async def health_v2(request: Request):
    return JSONResponse(status_code=200, content={"status": "ok", "api_version": "v2"})


app.include_router(v1_router)
app.include_router(v2_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=(ENV == "dev"))
