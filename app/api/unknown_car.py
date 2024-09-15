from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.base_config import current_active_user
from app.auth.database import get_async_session, User
from app.config import current_tz
from app.crud.unknown_car import create_unknown_car, get_unknown_cars
from app.schemas.unknown_car import UnknownCarResponse
from fastapi import APIRouter, Depends, Query, File, UploadFile, HTTPException, status
from aiocache import cached

router = APIRouter()


@router.post("/", response_model=UnknownCarResponse)
async def create_unknown_car_endpoint(
        number: str = Query(..., description="The number of the car", alias="car-number", example="unknown"),
        date: str = Query(
            ...,
            description="The date of the car",
            alias="car-date",
            example=f"{datetime.now(current_tz).strftime('%Y-%m-%d')}"),
        time: str = Query(
            ...,
            description="The time of the car",
            alias="car-time",
            example=f"{datetime.now(current_tz).strftime('%H:%M:%S')}"),
        db: AsyncSession = Depends(get_async_session),
        image: UploadFile = File(None),
        user: User = Depends(current_active_user)
):
    try:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        if not image:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is required")

        if len(date) != 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Date must be 10 characters and format YYYY-MM-DD")

        if len(time) != 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Time must be 8 characters and format HH:MM:SS")

        return await create_unknown_car(db=db, number=number, date=date, time=time, image=image)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
@cached(ttl=60)
async def get_unknown_cars_endpoint(
        db: AsyncSession = Depends(get_async_session),
        date: str = Query(
            ...,
            description="The date of the car",
            alias="car_date",
            example=f"{datetime.now(current_tz).strftime('%Y-%m')}"),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of items per page", alias="limit"),
        user: User = Depends(current_active_user)
    ):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_unknown_cars(db=db, date=date, page=page, limit=limit)


