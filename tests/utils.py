"""Вспомогательные функции для тестов"""

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement

from src.core.db.models import (
    Activity,
    Building,
    Organization,
    OrganizationPhone,
    organization_activities,
)

async def clear_database(db_session: AsyncSession) -> None:
    """Очистка БД"""

    await db_session.execute(delete(organization_activities))
    await db_session.execute(delete(OrganizationPhone))
    await db_session.execute(delete(Organization))
    await db_session.execute(delete(Building))
    await db_session.execute(delete(Activity))

    await db_session.commit()


async def insert_test_data(db_session: AsyncSession) -> None:
    activities = [
        Activity(id=1, name="Еда", level=1),
        Activity(id=2, name="Автомобили", level=1),
        Activity(id=3, name="Услуги", level=1),

        Activity(id=4, name="Мясная продукция", parent_id=1, level=2),
        Activity(id=5, name="Молочная продукция", parent_id=1, level=2),
        Activity(id=6, name="Легковые", parent_id=2, level=2),
        Activity(id=7, name="Грузовые", parent_id=2, level=2),
        Activity(id=8, name="Ремонт техники", parent_id=3, level=2),

        Activity(id=9, name="Запчасти", parent_id=6, level=3),
        Activity(id=10, name="Аксессуары", parent_id=6, level=3),
        Activity(id=11, name="Шиномонтаж", parent_id=8, level=3),
    ]

    db_session.add_all(activities)

    buildings = [
        Building(
            id=1,
            address="г. Москва, ул. Ленина, 1",
            location=WKTElement("POINT(37.617734 55.755864)", srid=4326),
        ),
        Building(
            id=2,
            address="г. Москва, ул. Тверская, 10",
            location=WKTElement("POINT(37.605469 55.764125)", srid=4326),
        ),
        Building(
            id=3,
            address="г. Москва, ул. Арбат, 12",
            location=WKTElement("POINT(37.598807 55.752023)", srid=4326),
        ),
        Building(
            id=4,
            address="г. Москва, ул. Профсоюзная, 45",
            location=WKTElement("POINT(37.540012 55.676095)", srid=4326),
        ),
    ]

    db_session.add_all(buildings)

    orgs = [
        Organization(id=1, name='ООО "Рога и Копыта"', building_id=1),
        Organization(id=2, name='ООО "Молочный мир"', building_id=2),
        Organization(id=3, name='Автоцентр "DrivePro"', building_id=3),
        Organization(id=4, name='Грузовой сервис "TruckMaster"', building_id=4),
        Organization(id=5, name='Сервисный центр "ТехноФикс"', building_id=2),
    ]

    db_session.add_all(orgs)

    phones = [
        OrganizationPhone(organization_id=1, phone="2-222-222"),
        OrganizationPhone(organization_id=1, phone="8-923-666-13-13"),
        OrganizationPhone(organization_id=2, phone="3-333-333"),
        OrganizationPhone(organization_id=3, phone="+7-495-111-22-33"),
        OrganizationPhone(organization_id=3, phone="+7-495-111-22-34"),
        OrganizationPhone(organization_id=4, phone="+7-495-222-33-44"),
        OrganizationPhone(organization_id=5, phone="+7-495-777-88-99"),
    ]

    db_session.add_all(phones)

    await db_session.flush()
    await db_session.execute(insert(organization_activities), [
        {"organization_id": 1, "activity_id": 4},
        {"organization_id": 1, "activity_id": 5},
        {"organization_id": 2, "activity_id": 5},
        {"organization_id": 3, "activity_id": 6},
        {"organization_id": 3, "activity_id": 9},
        {"organization_id": 3, "activity_id": 10},
        {"organization_id": 4, "activity_id": 7},
        {"organization_id": 4, "activity_id": 11},
        {"organization_id": 5, "activity_id": 8},
    ])

    await db_session.commit()