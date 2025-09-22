import random

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInfo, Breakfast


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


async def orm_add_breakfast(session: AsyncSession, data: dict):
    session.add(Breakfast(
        name_dish=data["name_dish"],
        calories=float(data["calories"]),
        proteins=float(data["proteins"]),
        fats=float(data["fats"]),
        carbohydrates=float(data["carbohydrates"]),
        description=data["description"]
    ))
    await session.commit()


async def orm_get_breakfast(session: AsyncSession):
    query = select(Breakfast).where(Breakfast.id == random.randint(1, 20))
    result = await session.execute(query)
    return result.scalars().all()


