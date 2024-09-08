from pydantic import BaseModel


class NumbersResponse(BaseModel):
    id: int
    number: str
