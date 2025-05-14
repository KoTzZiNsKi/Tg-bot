import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext

# Список вопросов и правильных ответов
QUESTIONS = [
    {"question": "Сколько будет 2 + 2?", "answer": "4"},
    {"question": "Столица Франции?", "answer": "Париж"},
    {"question": "Какой цвет у небес?", "answer": "голубой"},
]

# Переменная для подсчета баллов
score = 0

# Состояния для разговора
QUESTION, END = range(2)

def start(update: Update, context: CallbackContext) -> int:
    """Запуск бота и привествие"""
    update.message.reply_text('Привет! Напиши /test для начала теста.')
    return ConversationHandler.END

def test(update: Update, context: CallbackContext) -> int:
    """Запуск теста"""
    global score
    score = 0  # Сбросить баллы при начале нового теста
    update.message.reply_text(QUESTIONS[0]["question"])
    return QUESTION

def handle_answer(update: Update, context: CallbackContext) -> int:
    """Обработка ответа"""
    global score
    user_answer = update.message.text.lower()
    correct_answer = QUESTIONS[0]["answer"].lower()

    if user_answer == correct_answer:
        score += 1  # Увеличиваем баллы за правильный ответ

    # Удаляем вопрос, на который ответили
    QUESTIONS.pop(0)

    if len(QUESTIONS) > 0:
        # Если остались вопросы, задаём следующий
        update.message.reply_text(QUESTIONS[0]["question"])
        return QUESTION
    else:
        # Если вопросов больше нет, показываем результаты
        update.message.reply_text(f"Тест завершен! Ваши баллы: {score}")
        return END

def cancel(update: Update, context: CallbackContext) -> int:
    """Завершение теста"""
    update.message.reply_text("Тест завершен.")
    return ConversationHandler.END

def add_question(update: Update, context: CallbackContext) -> None:
    """Добавление нового вопроса"""
    if len(context.args) < 2:
        update.message.reply_text('Использование: /add_question <вопрос> <ответ>')
        return

    question = " ".join(context.args[:-1])
    answer = context.args[-1]

    QUESTIONS.append({"question": question, "answer": answer})
    update.message.reply_text(f"Вопрос добавлен: {question} - {answer}")

def show_questions(update: Update, context: CallbackContext) -> None:
    """Показ текущих вопросов"""
    if not QUESTIONS:
        update.message.reply_text('Вопросы ещё не добавлены.')
    else:
        question_list = "\n".join([f"{i+1}. {q['question']} - {q['answer']}" for i, q in enumerate(QUESTIONS)])
        update.message.reply_text(f"Текущие вопросы:\n{question_list}")

def delete_question(update: Update, context: CallbackContext) -> None:
    """Удаление вопроса"""
    if len(context.args) != 1:
        update.message.reply_text('Использование: /delete_question <номер вопроса>')
        return

    try:
        question_index = int(context.args[0]) - 1  # Переводим на индексацию с 0
        if 0 <= question_index < len(QUESTIONS):
            deleted_question = QUESTIONS.pop(question_index)
            update.message.reply_text(f"Вопрос удалён: {deleted_question['question']}")
        else:
            update.message.reply_text(f"Нет вопроса с номером {context.args[0]}.")
    except ValueError:
        update.message.reply_text('Неверный формат! Использование: /delete_question <номер вопроса>')

def main():
    """Основная настройка бота"""
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher

    # Настройка команд
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('test', test)],
        states={
            QUESTION: [MessageHandler(Filters.text & ~Filters.command, handle_answer)],
            END: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conversation_handler)
    dp.add_handler(CommandHandler('add_question', add_question))
    dp.add_handler(CommandHandler('show_questions', show_questions))
    dp.add_handler(CommandHandler('delete_question', delete_question))

    # Начать получение обновлений
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
