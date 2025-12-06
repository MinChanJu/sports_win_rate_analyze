from fastapi import APIRouter
from app.api.v1.endpoints import prediction, shooting

api_router = APIRouter()
api_router.include_router(prediction.router, tags=["prediction"])
api_router.include_router(shooting.router, tags=["shooting"])