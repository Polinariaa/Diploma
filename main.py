from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import json

# Эмуляция хранилища данных
chats_data = {}  # Словарь для хранения данных о чатах и их администраторах
(SELECTING_CHAT, SETTING_ADMINS) = range(2)

async def track_chat(update: Update, context: CallbackContext):
    # Обработка добавления в группу
    for member in update.message.new_chat_members:
        if member.username == context.bot.username:
            chat_id = update.message.chat_id
            chat_name = update.message.chat.title
            user_id = update.message.from_user.id
            if user_id not in chats_data:
                chats_data[user_id] = {}
            chats_data[user_id][chat_id] = chat_name
            print(f"Добавлен в чат: {chat_name}")

    # Обработка удаления из группы
    if update.message.left_chat_member:
        if update.message.left_chat_member.username == context.bot.username:
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            if user_id in chats_data and chat_id in chats_data[user_id]:
                del chats_data[user_id][chat_id]
                print(f"Удален из чата: {chat_id}")

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Настроить чат", callback_data='configure_chat')],
        [InlineKeyboardButton("Найти ответ на вопрос", callback_data='find_answer')],
        [InlineKeyboardButton("Привязать чат", callback_data='bind_chat')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет! Я ваш помощник для чатов, где могут задваться вопросы от пользователей!\n\n'
        'У меня есть две функции: \n'
        '1. Я умею реагировать на спам в чате и пересылать подозрительные сообщения администраторам чата\n'
        '2. Я умею искать ответы на вопросы по чату, если мне их задать\n\n'
        'Чтобы редактировать чат, где ты являешься администратором, нажми на кнопку "Настроить чат"\n'
        'Чтобы найти ответ на свой вопрос, нажми на кнопку "Найти ответ на вопрос"\n'
        'Чтобы привязать бот к чату для возможности настройки, нажми на кнопку "Привязать чат"',
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == 'bind_chat':
        if user_id in chats_data and chats_data[user_id]:
            keyboard = [
                [InlineKeyboardButton(chat_name, callback_data=f"select_chat_{chat_id}")]
                for chat_id, chat_name in chats_data[user_id].items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Отлично, мы нашли чаты, в которые вы добавили бота. Какой из них вы хотите привязать к боту?",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(text="К сожалению, не нашли чат, в который вы бы добавили бота. Добавьте бота и вернитесь к его привязке через основное меню.")

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