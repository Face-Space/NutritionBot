import random

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInfo, Breakfast, Snack


async def orm_add_user_info(session: AsyncSession, data: dict, user_id: int):
    session.add(UserInfo(
        user_id=user_id,
        age=data["age"],
        gender=data["gender"],
        weight=data["weight"],
        height=data["height"],
        activity_level=data["activity_level"],
        target=data["target"],
        food_prohibitions=data["food_prohibitions"]
    ))
    await session.commit()


async def orm_get_user_info(session: AsyncSession, user_id: int):
    query = select(UserInfo).where(UserInfo.user_id == int(user_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_user_info(session: AsyncSession, user_id: int):
    query = delete(UserInfo).where(UserInfo.user_id == int(user_id))
    await session.execute(query)
    await session.commit()


async def orm_get_breakfast(session: AsyncSession):
    count_result = await session.execute(select(func.count(Breakfast.id)))
    count = count_result.scalar_one()
    query = select(Breakfast).where(Breakfast.id == random.randint(1, count))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_snack(session: AsyncSession):
    count_result = await session.execute(select(func.count(Snack.id)))
    count = count_result.scalar_one()