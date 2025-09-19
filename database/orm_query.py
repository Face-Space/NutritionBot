from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInfo


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
