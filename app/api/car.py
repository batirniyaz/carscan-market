from fastapi import APIRouter, Depends, Query, UploadFile, File, status, HTTPException
from app.schemas.car import CarResponse
from app.auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.car import create_car

router = APIRouter()


@router.post("/", response_model=CarResponse)
async def create_car_endpoint(
        number: str = Query(..., description="The number of the car", alias="car-number", example="95A123BB"),
        date: str = Query(..., description="The date of the car", alias="car-date", example="2021-01-01"),
        time: str = Query(..., description="The time of the car", alias="car-time", example="12:00:00"),
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
