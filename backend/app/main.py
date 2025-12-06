from fastapi import FastAPI, HTTPException, Request, logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 설정
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

@app.middleware("http")
async def catch_all_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # FastAPI/Starlette 기본 HTTP 예외는 그대로 통과
        raise
    except Exception as e:
        # 여기서 로그 찍기 한줄로만
        logger.logger.error(f"Unhandled error:  {str(e)}")

        return JSONResponse(
            status_code=500,
            content={
                "detail": "서버 내부 에러가 발생했습니다.",
                "error": str(e),  # 개발 중에는 넣고, 운영에서는 빼는 게 좋음
            },
        )