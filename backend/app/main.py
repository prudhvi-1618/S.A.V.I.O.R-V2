from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from contextvars import ContextVar
import traceback
import logging

from app.api.v1 import processing, documents, chat
from app.core.logging import setup_logging, request_id_ctx_var, get_logger
from app.core.exceptions import SaviorException, VectorDatabaseError
from app.services.embeddings.qdrant_service import QdrantService

# Set up structured logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="S.A.V.I.O.R API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_ctx_var.set(request_id)
    
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}", exc_info=True)
        raise

@app.exception_handler(SaviorException)
async def savior_exception_handler(request: Request, exc: SaviorException):
    logger.error(f"SaviorException: {exc.message} - Status: {exc.status_code} - Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "details": exc.details},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected internal server error occurred."},
    )

app.include_router(processing.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "S.A.V.I.O.R API is running"}

@app.get("/health")
async def health():
    try:
        qdrant_health = QdrantService.health_check()
        status = "ok" if qdrant_health else "error"
        status_code = 200 if qdrant_health else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status = "error"
        status_code = 503
        qdrant_health = False

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "components": {
                "qdrant": "up" if qdrant_health else "down"
            }
        }
    )
