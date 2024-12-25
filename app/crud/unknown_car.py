import os
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import BASE_URL, AWS_ENDPOINT_URL
from app.models.unknown_car import UnknownCar
from app.utils.file_utils import s3_manager


async def create_unknown_car(db: AsyncSession, number: str, date: str, time: str, image: UploadFile):
    try:
        file_path = await s3_manager.upload_image(image=image, key=image.filename)
        image_url = f"{AWS_ENDPOINT_URL}{file_path}"

        db_unknown_car = UnknownCar(number=number, date=date, time=time, image_url=image_url)
        db.add(db_unknown_car)
        await db.commit()
        await db.refresh(db_unknown_car)

        db_unknown_car.image_url = f"{image_url}"

        return db_unknown_car
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_unknown_cars(db: AsyncSession, date: str, page: int = 1, limit: int = 10):
    query = select(UnknownCar)
    if len(date) == 10:
        query = query.filter_by(date=date).order_by(UnknownCar.time.desc())
    else:
        query = query.filter(UnknownCar.date.startswith(date)).order_by(UnknownCar.date.desc(), UnknownCar.time.desc())

    res = await db.execute(query.offset((page - 1) * limit).limit(limit))
    res_without_pagination = await db.execute(query)

    unknown_cars = res.scalars().all()
    unknown_cars_without_pagination = res_without_pagination.scalars().all()

    response = {"unknown_cars": [], "total_attendance": len(unknown_cars_without_pagination)}

    for unknown_car in unknown_cars:
        response["unknown_cars"].append(
            {
                "unknown_num": unknown_car.number,
                "attend_date": unknown_car.date,
                "attend_time": unknown_car.time,
                "image_url": unknown_car.image_url
            }
        )

    return response


async def delete_unknown_cars(db: AsyncSession):
    res = await db.execute(select(UnknownCar))
    cars = res.scalars().all()

    for car in cars:
        image_path = Path(car.image_url).name
        full_image_path = Path('app/storage') / image_path

        if full_image_path.exists():
            os.remove(full_image_path)
        else:
            print(f"File not found: {full_image_path}")

        await db.delete(car)

    await db.commit()
