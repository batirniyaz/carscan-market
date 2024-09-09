import datetime

from pydantic import BaseModel, Field


class DailyReportResponse(BaseModel):
    id: int = Field(..., description="The ID of the daily report")
    date: str = Field(..., description="The date of the daily report")
    top10: list = Field([], description="The top 10 cars of the daily report in general count")
    general_count: int = Field(0, description="The general count of the cars")
    overall_count: int = Field(0, description="The overall count of the cars")

    created_at: datetime.datetime = Field(..., description="The time the daily report was created")
    updated_at: datetime.datetime = Field(..., description="The time the daily report was updated")
