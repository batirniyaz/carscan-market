import os

import schedule
import asyncio
import pandas as pd

from fastapi import HTTPException, status
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import current_tz
from app.auth.database import get_async_session
from app.models.daily_report import DailyReport
from app.crud.car import get_cars, get_car

from app.config import START_TIME, END_TIME


async def define_date_type(db: AsyncSession, date: str):
    query = select(DailyReport)

    if len(date) == 10:
        result = await db.execute(query.filter_by(date=date))
        daily_report = result.scalars().first()
    else:
        result = await db.execute(query.filter(DailyReport.date.startswith(date)))
        daily_report = result.scalars().all()

    if not daily_report:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily report not found")

    return daily_report


async def get_daily_report(db: AsyncSession, date: str):

    daily_report = await define_date_type(db, date)

    return daily_report


async def store_daily_report():
    current_date = datetime.now(current_tz).strftime("%Y-%m-%d")

    async for session in get_async_session():
        async with session.begin():
            response = await get_cars(db=session, page=1, limit=10, date=current_date)

            top10 = response["top10"]
            total_cars = response["total_cars"]
            all_cars = response["all_cars"]

            top10_cars = []
            for car in top10:
                if car["attend_count"] > 2:
                    if START_TIME <= car["attend_time"] <= END_TIME:
                        top10_cars.append(car)

            general_cars = []
            for car in all_cars:
                if car["attend_count"] > 2:
                    if START_TIME <= car["attend_time"] <= END_TIME:
                        general_cars.append(car)

            daily_report = DailyReport(
                date=current_date,
                top10=top10_cars,
                general=general_cars,
                general_count=len(general_cars),
                overall_count=total_cars
            )

            session.add(daily_report)


def schedule_daily_report():
    schedule.every().day.at("23:55").do(lambda: asyncio.create_task(store_daily_report()))


async def create_excel_report(db: AsyncSession, date: str):

    daily_report = await define_date_type(db, date)
    daily_report_car_numbers = [car["car_number"] for car in daily_report.general]

    if len(date) == 10:
        data = await get_car(db=db, date=date, page=None, limit=None, car_number=None)
        formated_data = [car if car["car_number"] in daily_report_car_numbers else None for car in data]
        formated_response = []
        for car in formated_data:
            if car is not None:
                for attend in daily_report.general:
                    if attend["car_number"] == car["car_number"]:
                        formated_response.append(
                            {
                                "car_number": car["car_number"],
                                "attend_count": attend["attend_count"],
                                "first_time": car["first_time"],
                                "last_time": car["last_time"],
                            }
                        )

        df = pd.DataFrame(formated_response)
        reports_dir = "app/reports"

        excel_file_path = os.path.join(reports_dir, f"daily_report_{date}.xlsx")
        df.to_excel(excel_file_path, index=False)

        return excel_file_path
    else:
        # create excel report for the given month
        return


async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


schedule_daily_report()
asyncio.create_task(run_scheduler())
