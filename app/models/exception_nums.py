from sqlalchemy.orm import Mapped, mapped_column

from app.auth.database import Base


class Number(Base):
    __tablename__ = 'number'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[str] = mapped_column()


class StartEndTime(Base):
    __tablename__ = 'start_end_time'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_time: Mapped[str] = mapped_column(default='07:00')
    end_time: Mapped[str] = mapped_column(default='19:00')
