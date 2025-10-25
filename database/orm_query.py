from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInfo, TemporaryStorage, PaidUsers


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


async def orm_save_temporary_info(session: AsyncSession, data: dict, user_id: int):
    session.add(TemporaryStorage(
        user_id = user_id,
        message_meal_name = data["message_meal_name"],
        meal_info = data["meal_info"],
        meal_calories = data["meal_calories"],
        meal_weight = data["meal_weight"],
        food_intake = data["food_intake"]
    ))
    await session.commit()


async def orm_get_temporary_dish_info(session: AsyncSession, user_id: int, food_intake: str):
    query = select(TemporaryStorage).where(TemporaryStorage.user_id == int(user_id), TemporaryStorage.food_intake == str(food_intake))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_temporary_dish(session: AsyncSession, user_id: int):
    query = delete(TemporaryStorage).where(TemporaryStorage.user_id == int(user_id))
    await session.execute(query)
    await session.commit()


async def orm_get_paid_users(session: AsyncSession, user_id: int):
    query = select(PaidUsers).where(PaidUsers.user_id == int(user_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_mark_user_paid(session: AsyncSession, user_id: int):
    session.add(PaidUsers(user_id=int(user_id)))
    await session.commit()

