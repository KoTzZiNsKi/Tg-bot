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

# Список вопросов
QUESTIONS = [
    {
        "question": "Сколько будет 2 + 2?",
        "options": ["3", "4", "5"],
        "answer": "4"
    },
    {
        "question": "Столица Франции?",
        "options": ["Берлин", "Париж", "Мадрид"],
        "answer": "Париж"
    }
]

score = 0
QUESTION = 0


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /test чтобы начать тест.")


# Команда /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global score
    score = 0
    context.user_data["questions"] = QUESTIONS.copy()
    context.user_data["current_index"] = 0
    context.user_data["question_count"] = len(QUESTIONS)
    await send_next_question(update, context)
    return QUESTION


# Отправка следующего вопроса
async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["current_index"]
    if index < len(context.user_data["questions"]):
        q = context.user_data["questions"][index]
        reply_markup = ReplyKeyboardMarkup(
            [[opt] for opt in q["options"]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        await update.message.reply_text(q["question"], reply_markup=reply_markup)
    else:
        total = context.user_data["question_count"]
        points = round((score / total) * 10, 1)
        await update.message.reply_text(
            f"Тест завершён! Вы набрали {points} из 10 баллов.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


# Обработка ответа
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global score
    index = context.user_data["current_index"]
    user_answer = update.message.text
    correct = context.user_data["questions"][index]["answer"]

    if user_answer == correct:
        score += 1

    context.user_data["current_index"] += 1
    return await send_next_question(update, context)


# Отмена теста
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Команда /add_question
async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    parts = text.split("|")

    if len(parts) != 5:
        await update.message.reply_text(
            "Неверный формат.\nИспользуй: /add_question Вопрос | Вариант1 | Вариант2 | Вариант3 | Правильный"
        )
        return

    question = parts[0].strip()
    options = [parts[1].strip(), parts[2].strip(), parts[3].strip()]
    correct = parts[4].strip()

    if correct not in options:
        await update.message.reply_text("Правильный ответ должен быть одним из предложенных вариантов.")
        return

    QUESTIONS.append({
        "question": question,
        "options": options,
        "answer": correct
    })

    await update.message.reply_text(f"✅ Вопрос добавлен:\n{question}\n🧩 Варианты: {', '.join(options)}\n✅ Правильный: {correct}")


# Команда /show_questions
async def show_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUESTIONS:
        await update.message.reply_text("Список вопросов пуст.")
    else:
        msg = ""
        for i, q in enumerate(QUESTIONS, 1):
            msg += f"{i}. {q['question']} — Ответ: {q['answer']}\n"
        await update.message.reply_text(msg)


# Команда /delete_question
async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Используй: /delete_question <номер>")
        return

    index = int(context.args[0]) - 1
    if 0 <= index < len(QUESTIONS):
        removed = QUESTIONS.pop(index)
        await update.message.reply_text(f"🗑 Удалён вопрос: {removed['question']}")
    else:
        await update.message.reply_text("❌ Неверный номер вопроса.")


# Главная функция
async def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("test", test)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_question", add_question))
    app.add_handler(CommandHandler("show_questions", show_questions))
    app.add_handler(CommandHandler("delete_question", delete_question))

    await app.run_polling()


# 🔧 Обработка запуска под Render
if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
