# Основной файл, содержащий запуск бота и регистрацию обработчиков.
import asyncio
import logging
from database import create_table
from handlers import dp
from config import bot
import nest_asyncio
nest_asyncio.apply()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())