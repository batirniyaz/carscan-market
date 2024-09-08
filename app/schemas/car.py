import datetime

from pydantic import BaseModel, Field
from typing import Optional


class CarBase(BaseModel):
    number: str = Field(..., description="The number of the car")
    date: str = Field(..., description="The date of the car")
    time: str = Field(..., description="The time of the car")
    image_url: Optional[str] = Field(None, description="The image URL of the car")


class CarCreate(CarBase):
    pass


class CarResponse(CarBase):
    id: int = Field(..., description="The ID of the car")
    created_at: datetime.datetime = Field(..., description="The time the car was created")
    updated_at: datetime.datetime = Field(..., description="The time the car was updated")

    class Config:
        from_attributes = True
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "number": "95A123AA",
                "date": "2022-01-01",
                "time": "12:00",
                "image_url": "http://example.com/image.jpg",
                "created_at": "2022-01-01T12:00:00",
                "updated_at": "2022-01-01T12:00:00"
            }
        }
