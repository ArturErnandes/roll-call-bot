from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from config import db_data
from logger import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    f'postgresql+asyncpg://{db_data.admin}:{db_data.password}@{db_data.host}:{db_data.port}/{db_data.db_name}')

new_session = async_sessionmaker(engine, expire_on_commit=False)