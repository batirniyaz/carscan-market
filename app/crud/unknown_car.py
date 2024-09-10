from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.file_utils import save_upload_file
from app.models.unknown_car import UnknownCar
from app.config import BASE_URL


async def create_unknown_car(db: AsyncSession, number: str, date: str, time: str, image: UploadFile):
    try:
        main_image_url = f"/storage/"
        file_path = save_upload_file(image)
        image_url = f"{main_image_url}{file_path}"

        db_unknown_car = UnknownCar(number=number, date=date, time=time, image_url=image_url)
        db.add(db_unknown_car)
        await db.commit()
        await db.refresh(db_unknown_car)

        db_unknown_car.image_url = f"{BASE_URL}{image_url}"

        return db_unknown_car
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))