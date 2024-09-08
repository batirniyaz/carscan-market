from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils.file_utils import save_upload_file
from app.config import BASE_URL
from app.models.car import Car


async def create_car(db: AsyncSession, number: str, date: str, time: str, image: UploadFile):
    try:
        main_image_url = f"/storage/"
        file_path = save_upload_file(image)
        image_url = f"{main_image_url}{file_path}"

        db_car = Car(number=number, date=date, time=time, image_url=image_url)
        db.add(db_car)
        await db.commit()
        await db.refresh(db_car)

        db_car.image_url = f"{BASE_URL}{image_url}"

        return db_car
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
