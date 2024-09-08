from fastapi import APIRouter
from .car import router as car_router
from .exception_nums import router as exception_nums_router

router = APIRouter()

router.include_router(car_router, prefix="/car", tags=["Car"])
router.include_router(exception_nums_router, prefix="/exception-nums", tags=["Exception Numbers"])
