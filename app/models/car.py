import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.database import Base


class Car(Base):
    __tablename__ = 'car'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[str] = mapped_column()
    date: Mapped[str] = mapped_column()
    time: Mapped[str] = mapped_column()
    image_url: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc),
                                                          onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
