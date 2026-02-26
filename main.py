import asyncio

from bot import bot, dp
from logger import get_logger


logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Запуск бота")
    asyncio.run(dp.start_polling(bot))