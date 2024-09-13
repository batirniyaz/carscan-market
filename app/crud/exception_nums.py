from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.exception_nums import Number, StartEndTime
from app.models.car import Car
from app.config import BASE_URL


async def create_exception_num(db: AsyncSession, number: str):

    db_exception_num = Number(number=number)
    db.add(db_exception_num)
    await db.commit()
    await db.refresh(db_exception_num)
    return db_exception_num


async def get_exception_nums(db: AsyncSession):
    res = await db.execute(select(Number))
    return res.scalars().all()


async def delete_exception_num(db: AsyncSession, car_number: str):
    res = await db.execute(select(Number).filter_by(number=car_number))
    db_exception_num = res.scalar_one_or_none()
    if not db_exception_num:
        return {"detail": "Number not found"}
    await db.delete(db_exception_num)
    await db.commit()
    return {"detail": "Number deleted"}


async def search(db: AsyncSession):
    res = await db.execute(select(Car))
    cars = res.scalars().all()

    unique_numbers = set()
    unique_cars = set()
    for car in cars:
        if car.number not in unique_numbers:
            unique_numbers.add(car.number)

        if car not in unique_cars:
            unique_cars.add(car)

    last_attendance = {}
    for unique_car in unique_cars:
        if unique_car.number not in last_attendance:
            last_attendance[unique_car.number] = {"date": unique_car.date, "time": unique_car.time}
        else:
            current_last = last_attendance[unique_car.number]
            if unique_car.date > current_last["date"] or (
                    unique_car.date == current_last["date"] and unique_car.time > current_last["time"]):
                last_attendance[unique_car.number] = {
                    "date": unique_car.date,
                    "time": unique_car.time,
                    "image_url": f"{BASE_URL}{unique_car.image_url}"
                }

    response = []
    for unique_number in unique_numbers:
        response.append(
            {
                "number": unique_number,
                "last_attendance": last_attendance[unique_number]
            }
        )
    return response


async def create_start_end_time(db: AsyncSession, start_time: str, end_time: str):
    db_start_end_time = StartEndTime(start_time=start_time, end_time=end_time)
    db.add(db_start_end_time)
    await db.commit()
    await db.refresh(db_start_end_time)

    return db_start_end_time


async def get_start_end_time(db: AsyncSession):
    res = await db.execute(select(StartEndTime).limit(1))
    return res.scalar_one_or_none()


async def update_start_end_time(db: AsyncSession, start_time: str, end_time: str):
    res = await db.execute(select(StartEndTime).limit(1))
    db_start_end_time = res.scalar_one_or_none()
    if not db_start_end_time:
        return {"detail": "Time not found"}

    db_start_end_time.start_time = start_time
    db_start_end_time.end_time = end_time
    await db.commit()

    return db_start_end_time


