import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import logging
import sqlite3

# 🔐 Токен бота
TOKEN = "8080446742:AAHvpyBhyMqxsBNNz-fCt9pkPaj_Q1nHw1g"

# Ваш Telegram ID
AUTHORIZED_USER_ID = 5428660796

# 🔧 Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('questions.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🎓 Константы
QUESTION = 0

# 🟢 Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /test чтобы начать тест.")

# 🧪 Начать тест
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["score"] = 0
    context.user_data["current_index"] = 0
    await send_next_question(update, context)
    return QUESTION

# 📩 Следующий вопрос
async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["current_index"]
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()

    if index < len(questions):
        q = questions[index]
        reply_markup = ReplyKeyboardMarkup(
            [[q['option1'], q['option2'], q['option3']]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        await update.message.reply_text(q['question'], reply_markup=reply_markup)
    else:
        total = len(questions)
        correct = context.user_data["score"]
        points = round((correct / total) * 10, 1)
        await update.message.reply_text(
            f"🧾 Тест завершён!\n🎯 Ваш результат: {points} из 10.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

# ✅ Обработка ответа
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["current_index"]
    user_answer = update.message.text.strip()
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()

    correct = questions[index]['answer']
    if user_answer == correct:
        context.user_data["score"] += 1

    context.user_data["current_index"] += 1
    return await send_next_question(update, context)

# ❌ Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ➕ Добавление вопроса
async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ У вас нет прав для добавления вопросов.")
        return

    text = " ".join(context.args)
    parts = text.split("|")

    if len(parts) != 5:
        await update.message.reply_text(
            "Неверный формат.\nПример:\n/add_question Вопрос | Вариант1 | Вариант2 | Вариант3 | Правильный"
        )
        return

    question = parts[0].strip()
    options = [parts[1].strip(), parts[2].strip(), parts[3].strip()]
    correct = parts[4].strip()

    if correct not in options:
        await update.message.reply_text("❌ Правильный ответ должен быть одним из вариантов.")
        return

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO questions (question, option1, option2, option3, answer) VALUES (?, ?, ?, ?, ?)',
        (question, options[0], options[1], options[2], correct)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Вопрос добавлен:\n{question}\nВарианты: {', '.join(options)}\nПравильный: {correct}"
    )

# 📋 Показать все вопросы
async def show_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ У вас нет прав для просмотра вопросов.")
        return

    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()

    if not questions:
        await update.message.reply_text("Список вопросов пуст.")
    else:
        msg = ""
        for i, q in enumerate(questions, 1):
            msg += f"{i}. {q['question']} — ✅ Ответ: {q['answer']}\n"
        await update.message.reply_text(msg)

# 🗑 Удалить вопрос
async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ У вас нет прав для удаления вопросов.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Используй: /delete_question <номер>")
        return

    index = int(context.args[0]) - 1
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()

    if 0 <= index < len(questions):
        removed = questions[index]
        conn.execute('DELETE FROM questions WHERE id = ?', (removed['id'],))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"🗑 Удалён вопрос: {removed['question']}")
    else:
        conn.close()
        await update.message.reply
::contentReference[oaicite:25]{index=25}
 
