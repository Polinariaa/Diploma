from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_chat, delete_chat, save_message, get_admins_for_chat
from datetime import datetime
from suspicious_messages import is_suspicious
from bot_functions import add_admins, remove_admins
from answers import handle_search_query


async def track_chat(update: Update, context: CallbackContext):
    print("Я в хендлере трека чата")
    chat_id = update.message.chat_id
    chat_name = update.message.chat.title
    for member in update.message.new_chat_members:
        if member.username == context.bot.username:
            user_id = update.message.from_user.id
            add_chat(chat_id, chat_name, False, [user_id])
            print(f"Добавлен в чат: {chat_name}, администратор: {user_id}")

    # Обработка удаления из группы
    if update.message.left_chat_member:
        if update.message.left_chat_member.username == context.bot.username:
            delete_chat(chat_id)
            print(f"Удален из чата: {chat_id}")

async def start(update: Update, context: CallbackContext):
    print("Я в хендлере старта")
    if update.effective_chat.type != "private":
        return
    keyboard = [
        [InlineKeyboardButton("Привязать чат", callback_data='bind_chat')],
        [InlineKeyboardButton("Настроить чат", callback_data='configure_chat')],
        [InlineKeyboardButton("Найти ответ на вопрос", callback_data='find_answer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет! Я ваш помощник для чатов, где могут задваться вопросы от пользователей!\n\n'
        'У меня есть две функции: \n'
        '1. Я умею реагировать на спам в чате и пересылать подозрительные сообщения администраторам чата\n'
        '2. Я умею искать ответы на вопросы по чату, если мне их задать\n\n'
        'Чтобы редактировать чат, где ты являешься администратором, нажми на кнопку "Настроить чат"\n'
        'Чтобы найти ответ на свой вопрос, нажми на кнопку "Найти ответ на вопрос"\n'
        'Чтобы привязать бот к чату для возможности настройки, нажми на кнопку "Привязать чат"\n\n'
        'Важно добавить бота в администраторы канала, чтобы была возможность привязать его',
        reply_markup=reply_markup
    )

async def handle_text(update, context):
    print("Я в хендлере текста")
    text = update.message.text
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    message_id = update.message.message_id
    chat_name = update.message.chat.title
    timestamp = datetime.now()
    chat_type = update.message.chat.type

    if chat_type in ["group", "supergroup"]:
        # Сохраняем все сообщения в базу данных
        save_message(chat_id, message_id, text, timestamp)

        if is_suspicious(text):
            admins = get_admins_for_chat(chat_id)  # Получаем список администраторов для данного чата
            for admin in admins:
                try:
                    context.bot.forward_message(chat_id=admin, from_chat_id=chat_id, message_id=message_id)
                    context.bot.send_message(chat_id=admin, text=f"Подозрительное сообщение в чате {chat_name}")
                except Exception as e:
                    print(f"Не удалось переслать сообщение администратору {admin}: {str(e)}")

    else:
        action = context.user_data.get('action')
        search_chat_id = context.user_data.get('search_chat_id')

        if action == 'add':
            await add_admins(update, context)
        elif action == 'remove':
            await remove_admins(update, context)
        elif search_chat_id:
            await handle_search_query(update, context)
        else:
            # Если действие не установлено, не обрабатываем текст
            await update.message.reply_text("Пожалуйста, выберите действие из меню.")