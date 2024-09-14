import time
from datetime import datetime
from app.config import current_tz

from fastapi import APIRouter, Depends, Query, UploadFile, File, status, HTTPException, Response
from app.schemas.car import CarResponse
from app.auth.database import get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.car import create_car, get_cars, get_car

from app.auth.base_config import current_active_user

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
        image: UploadFile = File(None),
        user: User = Depends(current_active_user)
):
    try:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

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
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_cars(db=db, page=page, limit=limit, date=day)


@router.get("/month")
async def get_cars_endpoint(
        response: Response,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        month: str = Query(
            datetime.now(current_tz).strftime("%Y-%m"),
            description="The date should be in format MM",
            alias="month",
        ),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    start_time = time.time()

    cars_start_time = time.time()
    cars_data = await get_cars(db=db, page=page, limit=limit, date=month)
    cars_duration = (time.time() - cars_start_time) * 1000

    total_duration = (time.time() - start_time) * 1000

    response.headers["Server-Timing"] = (
        f"external_numbers;dur={cars_data['timing']['external_query_duration']:.2f}, "
        f"car_calculations;dur={cars_data['timing']['attendance_duration']:.2f}, "
        f"car_from_db;dur={cars_data['timing']['query_duration']:.2f}, "
        f"total;dur={total_duration:.2f}"
    )

    return cars_data


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
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

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
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not car_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Car number is required")

    if not page and limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page and limit are required")

    return await get_car(db=db, page=page, limit=limit, car_number=car_number, date=date)
