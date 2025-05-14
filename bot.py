from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
from datetime import datetime
import os

QUESTIONS = [
    {"question": "1. Столица Франции?", "options": ["Париж", "Берлин", "Лондон"], "answer": "Париж"},
    {"question": "2. 2 + 2 = ?", "options": ["3", "4", "5"], "answer": "4"},
    {"question": "3. Цвет неба?", "options": ["Синий", "Зелёный", "Красный"], "answer": "Синий"}
]

START_TEST, ASK_QUESTION = range(2)
user_data = {}
SAVE_FILE = "results.json"
ADMINS = [123456789]  # Замените на свой Telegram ID

def save_result(user_id, score):
    result = {
        "user_id": user_id,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(result)

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Начать тест"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Привет! Нажми 'Начать тест', чтобы приступить.", reply_markup=reply_markup)
    return START_TEST

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"score": 0, "current_q": 0}
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    progress = user_data[user_id]
    q_index = progress["current_q"]

    if q_index < len(QUESTIONS):
        question = QUESTIONS[q_index]
        keyboard = [[opt] for opt in question["options"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(question["question"], reply_markup=reply_markup)
        return ASK_QUESTION
    else:
        score = progress["score"]
        final_score = round((score / len(QUESTIONS)) * 10, 1)
        save_result(user_id, final_score)

        # Отправить результат админу
        for admin_id in ADMINS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📥 Новый результат:\nID: {user_id}\nБалл: {final_score} / 10"
            )

        keyboard = [["Пройти ещё раз"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"✅ Тест завершён! Ваш результат: {final_score} / 10",
            reply_markup=reply_markup
        )
        return START_TEST

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    answer = update.message.text
    progress = user_data[user_id]
    q_index = progress["current_q"]
    correct_answer = QUESTIONS[q_index]["answer"]

    if answer == correct_answer:
        progress["score"] += 1

    progress["current_q"] += 1
    return await ask_question(update, context)

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("⛔️ У вас нет доступа к этой команде.")
        return

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if not data:
        await update.message.reply_text("Пока нет результатов.")
        return

    text = "📊 Последние 10 результатов:\n\n"
    for i, r in enumerate(data[-10:], start=1):
        time = r["timestamp"].replace("T", " ").split(".")[0]
        text += f"{i}) ID: {r['user_id']}, Балл: {r['score']} / 10, Время: {time}\n"

    await update.message.reply_text(text)

async def clear_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("⛔️ У вас нет доступа к этой команде.")
        return

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

    await update.message.reply_text("🗑️ Все результаты были удалены.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест прерван.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("❌ Установите переменную окружения TOKEN")
        return

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_TEST: [MessageHandler(filters.Regex("^(Начать тест|Пройти ещё раз)$"), start_test)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("results", show_results))
    app.add_handler(CommandHandler("clear_results", clear_results))

    print("✅ Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()