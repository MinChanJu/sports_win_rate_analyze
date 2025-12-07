import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router
from app.core.config import settings
import time

app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
  return {"message": "Sports Win Rate Analysis API"}

logger = logging.getLogger("uvicorn.error")

@app.middleware("http")
async def catch_all_exceptions(request: Request, call_next):
  try:
    response = await call_next(request)
    return response
  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Unhandled error:  {str(e)}")

    return JSONResponse(
      status_code=500,
      content={
        "detail": "서버 내부 에러가 발생했습니다.",
        "error": str(e),
      },
    )
    
@app.middleware("http")
async def log_request_time(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  process_time = time.time() - start_time
  logger.info(f"Request: {request.method} {request.url} completed in {process_time*1000:.2f} milliseconds")
  return response