"""Модели базы данных"""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geography

# Система координат WGS84 (GPS)
SRID_WGS84 = 4326

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class Building(Base):
    """Модель здания""" 

    __tablename__ = "buildings"

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Адрес",
    )

    location: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=SRID_WGS84),
        nullable=False,
        comment="Географическая точка",
    )


class Organization(Base):
    """Модель организации"""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название",
    )

    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID здания",
    )


class OrganizationPhone(Base):
    """Модель телефона организации"""

    __tablename__ = "organization_phones"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID организации",
    )

    phone: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Телефон",
    )


class Activity(Base):
    """Модель деятельности"""

    __tablename__ = "activities"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название",
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        comment="ID вышестоящей по уровню записи",
    )

    level: Mapped[int] = mapped_column(
        nullable=False,
        comment="Уровень активности (1-3)",
    )

    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 3", name="chk_activity_level"),
    )


# Таблица связи многие-ко-многим между организациями и активностями
organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)