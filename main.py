from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os
from dotenv import load_dotenv

from bot_init import track_chat, handle_text, help, settings
from bot_functions import handle_button
from answers import handle_faq_text, find_answer

load_dotenv()

def create_application(token):
    application = Application.builder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('settings', settings))
    application.add_handler(CommandHandler('find_answer', find_answer))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_faq_text))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_chat))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, track_chat))

    return application

def main():
    # Создаем приложение
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN or TOKEN == 'your_telegram_bot_token_here':
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")
    application = create_application(TOKEN)
    # Запускаем приложение
    application.run_polling()


if __name__ == '__main__':
    main()