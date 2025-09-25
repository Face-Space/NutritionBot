from sqlalchemy import DateTime, func, String, Text, Float
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
    food_prohibitions: Mapped[str] = mapped_column(Text)


class Breakfast(Base):
    __tablename__ = "breakfast"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_dish: Mapped[str] = mapped_column(Text)
    calories: Mapped[float] = mapped_column(Float)
    proteins: Mapped[float] = mapped_column(Float)
    fats: Mapped[float] = mapped_column(Float)
    carbohydrates: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)


class Snack(Base):
    __tablename__ = "snack"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_dish: Mapped[str] = mapped_column(Text)
    calories: Mapped[int] = mapped_column(Float)
    proteins: Mapped[int] = mapped_column(Float)
    fats: Mapped[int] = mapped_column(Float)
    carbohydrates: Mapped[int] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)


class Dinner(Base):
    __tablename__ = "dinner"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_dish: Mapped[str] = mapped_column(Text)
    calories: Mapped[int] = mapped_column(Float)
    proteins: Mapped[int] = mapped_column(Float)
    fats: Mapped[int] = mapped_column(Float)
    carbohydrates: Mapped[int] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)


class EveningMeal(Base):
    __tablename__ = "evening_meal"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_dish: Mapped[str] = mapped_column(Text)
    calories: Mapped[int] = mapped_column(Float)
    proteins: Mapped[int] = mapped_column(Float)
    fats: Mapped[int] = mapped_column(Float)
    carbohydrates: Mapped[int] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)