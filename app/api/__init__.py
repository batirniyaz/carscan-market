from fastapi import APIRouter
from .car import router as car_router
from .exception_nums import router as exception_nums_router
from .export_data import router as export_data_router
from .daily_report import router as daily_report_router
from .unknown_car import router as unknown_car_router

router = APIRouter()

router.include_router(car_router, prefix="/car", tags=["Car"])
router.include_router(unknown_car_router, prefix="/unknown-car", tags=["Unknown Car"])
router.include_router(exception_nums_router, prefix="/exception-nums", tags=["Exception Numbers"])
router.include_router(export_data_router, prefix="/export-data", tags=["Export Data"])
router.include_router(daily_report_router, prefix="/daily-report", tags=["Daily Report"])

