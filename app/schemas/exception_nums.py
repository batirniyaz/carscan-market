from pydantic import BaseModel


class NumbersResponse(BaseModel):
    id: int
    number: str


class StartEndTimeResponse(BaseModel):
    id: int
    start_time: str = '07:00'
    end_time: str = '19:00'
