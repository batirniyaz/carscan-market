from sqlalchemy.orm import Mapped, mapped_column

from app.auth.database import Base


class Number(Base):
    __tablename__ = 'number'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[str] = mapped_column()
