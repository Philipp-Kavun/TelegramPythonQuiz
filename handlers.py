# Файл, содержащий обработчики команд (/start, /quiz) и 
# callback-запросов (ответы на вопросы квиза)

from aiogram import F, Dispatcher, types
from aiogram.filters.command import Command
from database import get_quiz_index, update_quiz_index
from quiz_data import quiz_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards import generate_options_keyboard
#import sqlite3

# Диспетчер
dp = Dispatcher()

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    
    # # Увеличиваем количество правильных ответов
    # correct_answers = await get_quiz_results(callback.from_user.id)
    # correct_answers += 1
    # await update_quiz_results(callback.from_user.id, correct_answers)
    
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    results = 0
    await update_quiz_index(user_id, current_question_index, results)
    await get_question(message, user_id)

#from database import get_quiz_statistics

# @dp.message(Command(commands=['stats']))
# async def send_quiz_statistics(message: types.Message):
#     user_id = message.from_user.id
#     question_index = await get_quiz_statistics(user_id)
    
#     if question_index is not None:
#         await message.reply(f"Ваш текущий прогресс в квизе: вопрос {question_index}.")
#     else:
#         await message.reply("Вы еще не начали квиз.")