from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from config import db_data
from classes import User
from logger import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    f'postgresql+asyncpg://{db_data.admin}:{db_data.password}@{db_data.host}:{db_data.port}/{db_data.db_name}')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_users_list_db():
    query = text("SELECT * FROM users")

    async with new_session() as session:
        try:
            result = await session.execute(query)
            users_list: list[User] = []

            for row in result:
                users_list.append(User(
                    id = row.user_id,
                    name = row.name,
                ))
            logger.info("Список группы успешно получен")
            return users_list

        except Exception as e:
            logger.error(f"Ошибка при получении списка группы: {str(e)}")
            return []