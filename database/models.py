from sqlalchemy import DateTime, func, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class UserInfo(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    age: Mapped[int] = mapped_column()
    gender: Mapped[str] = mapped_column(String(10))
    weight: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    activity_level: Mapped[str] = mapped_column(String(8))
    target: Mapped[str] = mapped_column(String(12))

