"""Точка входа в приложение"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.organizations.router import router as organizations_router
from src.core.db.db_manager import get_database_manager

# Только для заполнения тестовыми данными
from tests.utils import clear_database, insert_test_data


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with get_database_manager().session_factory() as session:
        await clear_database(session)
        await insert_test_data(session)

    yield

app = FastAPI(
    title="Organizations API",
    debug=False,
    lifespan=lifespan,
    description="API для работы с организациями",
)

api_router = APIRouter(prefix="/api")
api_router.include_router(organizations_router)
app.include_router(api_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)