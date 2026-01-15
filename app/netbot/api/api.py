from fastapi import APIRouter
from .endpoints import ping, chat

router = APIRouter()

router.include_router(ping.router, prefix="/v1", tags=["ping"])
router.include_router(chat.router, prefix="/v1", tags=["chat"])
