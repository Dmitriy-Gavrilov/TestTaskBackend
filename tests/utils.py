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
            address="г. Москва, ул. Ленина, 1",
            location=WKTElement("POINT(37.617734 55.755864)", srid=4326),
        ),
        Building(
            address="г. Москва, ул. Тверская, 10",
            location=WKTElement("POINT(37.605469 55.764125)", srid=4326),
        ),
        Building(
            address="г. Москва, ул. Арбат, 12",
            location=WKTElement("POINT(37.598807 55.752023)", srid=4326),
        ),
        Building(
            address="г. Москва, ул. Профсоюзная, 45",
            location=WKTElement("POINT(37.540012 55.676095)", srid=4326),
        ),
    ]

    db_session.add_all(buildings)
    await db_session.flush()

    orgs = [
        Organization(name='ООО "Рога и Копыта"', building_id=buildings[0].id),
        Organization(name='ООО "Молочный мир"', building_id=buildings[1].id),
        Organization(name='Автоцентр "DrivePro"', building_id=buildings[2].id),
        Organization(name='Грузовой сервис "TruckMaster"', building_id=buildings[3].id),
        Organization(name='Сервисный центр "ТехноФикс"', building_id=buildings[1].id),
    ]

    db_session.add_all(orgs)
    await db_session.flush()

    phones = [
        OrganizationPhone(organization_id=orgs[0].id, phone="+72222222222"),
        OrganizationPhone(organization_id=orgs[0].id, phone="+79236661313"),
        OrganizationPhone(organization_id=orgs[1].id, phone="+73333333333"),
        OrganizationPhone(organization_id=orgs[2].id, phone="+74951112233"),
        OrganizationPhone(organization_id=orgs[2].id, phone="+74951112234"),
        OrganizationPhone(organization_id=orgs[3].id, phone="+74952223344"),
        OrganizationPhone(organization_id=orgs[4].id, phone="+74957778899"),
    ]

    db_session.add_all(phones)
    await db_session.flush()

    await db_session.execute(insert(organization_activities), [
        {"organization_id": orgs[0].id, "activity_id": 4},
        {"organization_id": orgs[0].id, "activity_id": 5},
        {"organization_id": orgs[1].id, "activity_id": 5},
        {"organization_id": orgs[2].id, "activity_id": 6},
        {"organization_id": orgs[2].id, "activity_id": 9},
        {"organization_id": orgs[2].id, "activity_id": 10},
        {"organization_id": orgs[3].id, "activity_id": 7},
        {"organization_id": orgs[3].id, "activity_id": 11},
        {"organization_id": orgs[4].id, "activity_id": 8},
    ])

    await db_session.commit()