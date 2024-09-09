import datetime

from sqlalchemy import JSON, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.database import Base


class DailyReport(Base):
    __tablename__ = 'daily_report'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[str] = mapped_column()
    top10: Mapped[list[dict]] = mapped_column(JSON, default=[])
    general: Mapped[list[dict]] = mapped_column(JSON, default=[])
    general_count: Mapped[int] = mapped_column(default=0)
    overall_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                          default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                          default=lambda: datetime.datetime.now(datetime.timezone.utc),
                                                          onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
