import os
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.config import BASE_URL, AWS_ENDPOINT_URL, AWS_BUCKET_NAME, BASE_PATH
from app.crud.cars.car_processes import (
    process_attend_count
)
from app.models.car import Car
from app.utils.excel_file_utils import create_excel_file
from app.utils.file_utils import s3_manager


async def migrate_images_to_s3(db: AsyncSession):
    try:
        # Получение всех записей с локальным `image_url`
        query = select(Car).where(Car.image_url.like("/storage%"))
        result = await db.execute(query)
        cars = result.scalars().all()
        print(f"Найдено {len(cars)} записей с локальным `image_url`")
        for car in cars:
            local_path = f'{BASE_PATH}{car.image_url}'
            print(local_path)
            if not os.path.exists(local_path):
                continue

            # Генерация S3 ключа (например, используем имя файла)
            filename = os.path.basename(local_path)
            s3_key = filename

            # Загрузка файла в S3
            s3_url = await s3_manager.upload_file(file_path=local_path, key=s3_key, content_type="image/jpeg")

            # Обновление URL в базе данных
            car.image_url = str(os.path.join(AWS_ENDPOINT_URL, AWS_BUCKET_NAME, s3_url))
            print(f"Файл {local_path} перемещен в S3: {s3_url}")

            # Удаление локального файла (опционально)
            os.remove(local_path)

            await db.commit()

    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при миграции изображений: {e}")
        raise


async def create_car(db: AsyncSession, number: str, date: str, time: str, image: UploadFile):
    try:

        file_path = await s3_manager.upload_image(image=image, key=image.filename)
        image_url = os.path.join(AWS_ENDPOINT_URL, AWS_BUCKET_NAME, file_path)

        db_car = Car(number=number, date=date, time=time, image_url=str(image_url))
        db.add(db_car)
        await db.commit()
        await db.refresh(db_car)

        db_car.image_url = f"{image_url}"

        return db_car
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_car(
        db: AsyncSession,
        car_number: Optional[str],
        date: str,
        page: Optional[int] = 1,
        limit: Optional[int] = 10
):
    query = select(Car)
    stmt_without_pagination = None

    if not car_number:
        if len(date) == 10:
            stmt = query.filter_by(date=date)
        else:
            stmt = query.filter(Car.date.startswith(date))
    else:
        query = query.filter_by(number=car_number)

        if len(date) == 7:
            query = query.filter(Car.date.startswith(date))
            stmt_without_pagination = query.filter(Car.date.startswith(date))
        else:
            query = query.filter_by(date=date)
            stmt_without_pagination = query.filter_by(date=date)

        if limit and page:
            stmt = query.offset((page - 1) * limit).limit(limit)
        else:
            stmt = query

    result = await db.execute(stmt)
    cars_attendances = result.scalars().all()

    if stmt_without_pagination is not None:
        result_without_pagination = await db.execute(stmt_without_pagination)
        cars_attendances_without_pagination = result_without_pagination.scalars().all()
    else:
        cars_attendances_without_pagination = []

    if not cars_attendances:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car attendances not found")

    response = []

    sorted_cars_attendances = sorted(
        cars_attendances_without_pagination,
        key=lambda x: datetime.strptime(x.time, "%H:%M:%S"),
        reverse=True)

    first_attendances = {}
    last_attendances = {}

    if car_number and len(date) == 7:

        (attend_count,
         unique_cars,
         sorted_cars,
         attend_count_cars,
         attend_count_car) = process_attend_count(cars_attendances, cars_attendances_without_pagination)

        for car in cars_attendances_without_pagination:
            if car.date not in first_attendances:
                first_attendances[car.date] = car
            elif car.time < first_attendances[car.date].time:
                first_attendances[car.date] = car

            if car.date not in last_attendances:
                last_attendances[car.date] = car
            elif car.time > last_attendances[car.date].time:
                last_attendances[car.date] = car

        sorted_first_attendances = dict(
            sorted(first_attendances.items(), key=lambda item: item[0], reverse=True)
        )

        for date in sorted_first_attendances:
            response.append(
                {
                    "date": date,
                    "car_number": first_attendances[date].number,
                    "first_time": first_attendances[date].time,
                    "first_image": first_attendances[date].image_url,
                    "last_time": last_attendances[date].time,
                    "last_image": last_attendances[date].image_url,
                    "overall_count": attend_count_car[date][car_number]["count"] if date in attend_count_car else 0
                }
            )
    elif car_number and len(date) == 10:
        if limit is not None:
            special_response = {"cars": [], "overall_count": 0}

            for car in sorted_cars_attendances:
                special_response["cars"].append({
                    "time": car.time,
                    "image": car.image_url,
                })

                special_response["overall_count"] += 1
            return special_response

        else:

            for car in sorted_cars_attendances:
                response.append(
                    {
                        "time": car.time,
                        "image": car.image_url,
                    }
                )

    elif not car_number and len(date) == 10:
        unique_cars = set()
        for car in cars_attendances:
            if car.number not in unique_cars:
                unique_cars.add(car.number)
                first_attendances[car.number] = car
                last_attendances[car.number] = car
            else:
                if car.time < first_attendances[car.number].time:
                    first_attendances[car.number] = car
                if car.time > last_attendances[car.number].time:
                    last_attendances[car.number] = car

        for number in first_attendances:
            response.append(
                {
                    "car_number": number,
                    "first_time": first_attendances[number].time,
                    "first_image": first_attendances[number].image_url,
                    "last_time": last_attendances[number].time,
                    "last_image": last_attendances[number].image_url
                }
            )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date or cars format")

    return response


async def create_excel_car(db: AsyncSession, date: str, car_number: str):
    data = await get_car(db=db, car_number=car_number, date=date, page=None, limit=None)

    formated_data = []
    if data:
        if len(date) == 10:
            total = 0
            for car in data:
                formated_data.append({
                    "time": car["time"],
                    "image": car["image"],
                })
                total += 1

            formated_data.append({"time": "", "image": ""})

            formated_data.append({
                "time": car_number,
                "image": f"{total} days",
            })

        else:
            average_come = 0
            for car in data:
                formated_data.append({
                    "date": car["date"],
                    "overall_count": car["overall_count"],
                })
                average_come += car["overall_count"]

            formated_data.append({"date": "", "overall_count": ""})

            formated_data.append({
                "date": car_number,
                "overall_count": f"average {average_come / len(data)}",
            })

        excel_car = await create_excel_file(formated_data, file_name=f"car_{car_number}_date_{date}")

        return excel_car

    else:
        return formated_data
