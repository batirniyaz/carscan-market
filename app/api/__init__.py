from fastapi import APIRouter
from .car import router as car_router
from .exception_nums import router as exception_nums_router
from .export_data import router as export_data_router

router = APIRouter()

router.include_router(car_router, prefix="/car", tags=["Car"])
router.include_router(exception_nums_router, prefix="/exception-nums", tags=["Exception Numbers"])
router.include_router(export_data_router, prefix="/export-data", tags=["Export Data"])
