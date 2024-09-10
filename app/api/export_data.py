from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.daily_report import create_excel_report

from app.auth.database import get_async_session

router = APIRouter()


@router.get("/daily-report/")
async def export_data(date: str, db: AsyncSession = Depends(get_async_session)):

    file_data = await create_excel_report(db, date)
    return FileResponse(
        path=file_data,
        filename=f"report_{date}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
