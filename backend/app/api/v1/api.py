from fastapi import APIRouter
from app.api.v1.endpoints import game

api_router = APIRouter()
api_router.include_router(game.router, tags=["game"])