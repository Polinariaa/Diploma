from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_chat, delete_chat

async def track_chat(update: Update, context: CallbackContext):
    # Обработка добавления в группу
    for member in update.message.new_chat_members:
        if member.username == context.bot.username:
            chat_id = update.message.chat_id
            chat_name = update.message.chat.title
            user_id = update.message.from_user.id
            add_chat(chat_id, chat_name, False, [user_id])
            print(f"Добавлен в чат: {chat_name}, администратор: {user_id}")

    # Обработка удаления из группы
    if update.message.left_chat_member:
        if update.message.left_chat_member.username == context.bot.username:
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            delete_chat(chat_id)
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