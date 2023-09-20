import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, CallbackContext

TOKEN = "6527408683:AAH4KBh9bFOHrgjpMdAuxVDGO1UapMiNASI"

subject_names = {
    "english": "Англійська",
    "biology": "Біологія",
    "geography": "Географія",
    "foreign": "Іноземна мова",
    "history": "Історія",
    "informatics": "Інформатика",
    "algebra": "Алгебра",
    "geometry": "Геометрія",
    "literature": "Література",
    "ukrainian": "Українська мова",
    "physics": "Фізика",
    "chemistry": "Хімія",
    "arts": "Мистецтво",
    "defense": "Захист Вітчизни",
    "physed": "Фізичне виховання",
    "menu": "Меню"
}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

CHOOSING_SUBJECT, CHOOSING_TASK = range(2)

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    print("Handler XYZ is being called")  # Replace XYZ with the handler name
    update.message.reply_html(
        f"Вітання, {user.mention_html()}!\n"
        "Мене звуть Бот Ашот, я допомагатиму робити тобі тести. "
        "Для початку вибери предмет, який тобі потрібен:",
        reply_markup=get_subjects_keyboard(),
    )
    return CHOOSING_SUBJECT

def get_subjects_keyboard():
    keyboard = [[InlineKeyboardButton(name, callback_data=eng_name)] for eng_name, name in subject_names.items()]
    return InlineKeyboardMarkup(keyboard)

def choose_subject(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    subject = query.data.lower()
    context.user_data["subject"] = subject

    if subject == "menu":
        query.edit_message_text(
            "Вибери предмет, який тобі потрібен:",
            reply_markup=get_subjects_keyboard(),
        )
        return CHOOSING_SUBJECT

    query.edit_message_text(
        "Тепер вибери номер завдання, яке тобі потрібно:",
        reply_markup=get_task_numbers_keyboard(),
    )
    return CHOOSING_TASK

def get_task_numbers_keyboard():
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 11)],
        [InlineKeyboardButton("Меню", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def choose_task_number(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    task_number = query.data

    if task_number == "menu":
        query.edit_message_text(
            "Вибери предмет, який тобі потрібен:",
            reply_markup=get_subjects_keyboard(),
        )
        return CHOOSING_SUBJECT

    last_task_number = context.user_data.get("last_task_number")
    context.user_data["task_number"] = task_number

    if last_task_number != task_number:
        query.edit_message_text(
            f"Ти вибрав завдання номер {task_number}.",
            reply_markup=query.message.reply_markup
        )
        context.user_data["last_task_number"] = task_number
    else:
        query.message.reply_text(
            f"Ти вже вибрав завдання номер {task_number}. Вибери інше завдання або використовуй кнопку 'Меню' для повернення в меню."
        )
    return CHOOSING_TASK

def text_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Просто текстовое сообщение.")
    return ConversationHandler.END

def show_menu(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Меню:\n"
        "/start - Почати спілкування з ботом\n"
        "/help - Отримати допомогу"
    )

def show_help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Даний бот допомагає користувачам отримувати завдання з різних предметів для вивчення.\n"
        "Для початку виберіть предмет та номер завдання з клавіатурі бота.\n"
        "Якщо ви хочете повернутися в меню вибору предмету, використовуйте кнопку 'Меню' у клавіатурі бота."
    )

def unknown_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Невідома команда. Використовуйте /start для початку роботи з ботом.")

def error(update: Update, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")

def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("menu", show_menu))
    dispatcher.add_handler(CommandHandler("help", show_help))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_SUBJECT: [CallbackQueryHandler(choose_subject)],
            CHOOSING_TASK: [CallbackQueryHandler(choose_task_number)],
        },
        fallbacks=[],
        map_to_parent={
            CHOOSING_SUBJECT: ConversationHandler.END,
            CHOOSING_TASK: ConversationHandler.END,
        },
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()