from fastapi import APIRouter
from .sprites import router as sprites_router
from .audio import router as audio_router
from .scores import router as scores_router

router = APIRouter()

router.include_router(sprites_router)
router.include_router(audio_router)
router.include_router(scores_router)