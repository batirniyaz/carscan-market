from datetime import datetime
from app.config import current_tz

from fastapi import APIRouter, Depends, Query, UploadFile, File, status, HTTPException
from app.schemas.car import CarResponse
from app.auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.car import create_car, get_cars, get_car

router = APIRouter()


@router.post("/", response_model=CarResponse)
async def create_car_endpoint(
        number: str = Query(..., description="The number of the car", alias="car-number", example="95A123BB"),
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
        image: UploadFile = File(None)
):
    try:
        if not image:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is required")

        if len(number) != 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Number must be 8 characters and match example")

        if len(date) != 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Date must be 10 characters and format YYYY-MM-DD")

        if len(time) != 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Time must be 8 characters and format HH:MM:SS")

        return await create_car(db=db, number=number, date=date, time=time, image=image)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/day")
async def get_cars_endpoint(
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        day: str = Query(
            datetime.now(current_tz).strftime("%Y-%m-%d"),
            description="The date should be in format DD",
            alias="day",
        ),
):
    return await get_cars(db=db, page=page, limit=limit, date=day)


@router.get("/month")
async def get_cars_endpoint(
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        month: str = Query(
            datetime.now(current_tz).strftime("%Y-%m"),
            description="The date should be in format MM",
            alias="month",
        ),
):
    return await get_cars(db=db, page=page, limit=limit, date=month)


@router.get("/week")
async def get_cars_endpoint(
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        week: str = Query(
            datetime.now(current_tz).strftime("%Y-%W"),
            description="The date should be in format YYYY-WW",
            alias="week",
        ),
):
    return await get_cars(db=db, page=page, limit=limit, date=None, week=week)


@router.get("/{car_number}")
async def get_car_endpoint(
        car_number: str,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        date: str = Query(
            ...,
            description="The month or day of the car",
            alias="date",
            example=f"{datetime.now(current_tz).strftime('%Y-%m')}",
        ),
):
    return await get_car(db=db, page=page, limit=limit, car_number=car_number, date=date)
