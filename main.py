from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from database import get_chat, set_bot_active, get_user_admin_chats, get_admins_for_chat
from bot_init import track_chat, start
from bot_functions import handle_button

def main():
    TOKEN = '6714836351:AAGqOkFIRdr68t3skyhS6_d2l6Zn8D9ZBEc'

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_chat))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, track_chat))

    # Запускаем приложение
    application.run_polling()


if __name__ == '__main__':
    main()