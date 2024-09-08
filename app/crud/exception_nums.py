from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.exception_nums import Number


async def create_exception_num(db: AsyncSession, number: str):

    db_exception_num = Number(number=number)
    db.add(db_exception_num)
    await db.commit()
    await db.refresh(db_exception_num)
    return db_exception_num


async def get_exception_nums(db: AsyncSession):
    res = await db.execute(select(Number))
    return res.scalars().all()
