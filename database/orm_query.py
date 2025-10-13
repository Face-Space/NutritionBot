import random

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInfo, Breakfast, Snack, Dinner, EveningMeal


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


async def orm_get_random_dish(session: AsyncSession, model):
    query = select(model).order_by(func.random()).limit(1)
    # так гарантированно получим одну случайную запись из таблицы, вне зависимости от порядка или пропусков в id
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_dish_by_id(session: AsyncSession, model, dish_id):
    query = select(model).where(model.id == int(dish_id))
    result = await session.execute(query)
    return result.scalars().all()


# async def orm_get_dish_by_id(session: AsyncSession, table_name, dish_id: int):
#     query = select(table_name).where(table_name.id == int(dish_id))




