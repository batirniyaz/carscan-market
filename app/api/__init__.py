from fastapi import APIRouter
from .car import router as car_router

router = APIRouter()

router.include_router(car_router, prefix="/car", tags=["Car"])
