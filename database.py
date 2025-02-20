# Файл, содержащий функции для работы с базой данных 
# (создание таблицы, получение и обновление индекса вопроса).
import aiosqlite

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('CREATE TABLE IF NOT EXISTS quiz_bot (user_id INTEGER PRIMARY KEY, question_index INTEGER, quiz_result INTEGER DEFAULT 0)')
        # Сохраняем изменения
        await db.commit()

async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('''SELECT question_index, 
                              quiz_result 
                              FROM quiz_state 
                              WHERE user_id = (?)''', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index, results):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, quiz_result) VALUES (?, ?, ?)', (user_id, index, results))
        # Сохраняем изменения
        await db.commit()

# async def get_quiz_statistics(user_id):
#     async with aiosqlite.connect(DB_NAME) as db:
#         # Извлекаем данные о текущем индексе вопроса для данного пользователя
#         async with db.execute('SELECT question_index, quiz_result FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
#             results = await cursor.fetchone()
#             if results is not None:
#                 return results[0], results[1]  # Возвращаем оба значения
#             else:
#                 return 0, 0  # Возвращаем значения по умолчанию