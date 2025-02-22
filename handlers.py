# Файл, содержащий обработчики команд (/start, /quiz) и 
# callback-запросов (ответы на вопросы квиза)

from aiogram import F, Dispatcher, types
from aiogram.filters.command import Command
from database import get_quiz_index, update_quiz_index, update_user_score, get_user_score
from quiz_data import quiz_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards import generate_options_keyboard
#import sqlite3

# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    new_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_user_score(user_id, new_score)
    await get_question(message, user_id)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_score = await get_user_score(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1  
    # Увеличиваем количество правильных ответов  
    current_score += 1
    await update_user_score(callback.from_user.id, current_score)
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f'''Это был последний вопрос. Квиз завершен!
                                      \nВаш результат: {current_score} правильных ответов''')


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_score = await get_user_score(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_user_score(callback.from_user.id, current_score)
    


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f'''Это был последний вопрос. Квиз завершен!
                                      \nВаш результат: {current_score} правильных ответов''')

async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

# Хендлер на команду /help
@dp.message(Command('help'))
async def cmd_start(message: types.Message):
    await message.answer('Команды бота:\n\
                /start - начать взаимодействие с ботом\n\
                /help - открыть помощь\n\
                /quiz -начать игру')