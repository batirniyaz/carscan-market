from concurrent.futures import ThreadPoolExecutor

from app.crud.cars.car_processes import (
    process_last_attendances,
    process_last_attendances_without_pagination,
    process_attend_count,
    process_top10_response,
)


def call_processes(pag_cars, cars: list = None):
    with ThreadPoolExecutor() as executor:
        last_attendances_future = executor.submit(process_last_attendances, pag_cars)
        last_attendances_count_future = executor.submit(process_last_attendances_without_pagination, cars)
        attend_count_future = executor.submit(process_attend_count, cars, None)

        attend_count, unique_cars, sorted_cars, attend_count_cars, attend_count_car = attend_count_future.result()

        top10response_future = executor.submit(process_top10_response, sorted_cars, attend_count)

        last_attendances = last_attendances_future.result()
        last_attendances_count = last_attendances_count_future.result()
        top10response = top10response_future.result()

    return last_attendances, last_attendances_count, top10response, unique_cars
