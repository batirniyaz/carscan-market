from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.daily_report import create_excel_report
from app.crud.car import create_excel_car

from app.auth.database import get_async_session

router = APIRouter()


@router.get("/report/")
async def export_data_report(date: str, db: AsyncSession = Depends(get_async_session)):

    file_data = await create_excel_report(db, date)
    return FileResponse(
        path=file_data,
        filename=f"report_{date}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/car")
async def export_data_car(date: str, car_number: str, db: AsyncSession = Depends(get_async_session)):

    file_data = await create_excel_car(db, date, car_number=car_number)
    return FileResponse(
        path=file_data,
        filename=f"car_{car_number}_date_{date}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
