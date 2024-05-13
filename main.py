from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_init import track_chat, handle_text, help, settings, find_answer
from bot_functions import handle_button

def main():
    TOKEN = '6714836351:AAGqOkFIRdr68t3skyhS6_d2l6Zn8D9ZBEc'

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды start
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('settings', settings))
    application.add_handler(CommandHandler('find_answer', find_answer))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_chat))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, track_chat))

    # Запускаем приложение
    application.run_polling()


if __name__ == '__main__':
    main()