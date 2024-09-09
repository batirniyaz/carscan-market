from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_async_session
from datetime import datetime
from app.config import current_tz
from app.crud.daily_report import get_daily_report

router = APIRouter()


@router.get("/")
async def get_daily_report_endpoint(
        db: AsyncSession = Depends(get_async_session),
        date: str = Query(
            ...,
            alias="date",
            description="YYYY-MM-DD format",
            example=datetime.now(current_tz).strftime("%Y-%m"))
):
    return await get_daily_report(db, date)
