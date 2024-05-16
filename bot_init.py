from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_chat, delete_chat
from datetime import datetime
from suspicious_messages import is_suspicious, forward_suspicious_message, process_spam_keywords
from manage_bot_admins import add_admins, remove_admins
from answers import handle_faq_text


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

async def help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        return
    help_message = (
        "Привет! Я ваш бот-помощник для чатов!\n\n"
        "У меня есть 2 основные функции:\n"
        "- Реагирование на спам в чатах\n"
        "- Ответы на вопросы по чату\n\n"
        "Если ты администратор, введи команду /settings для настройки или привязки чата.\n"
        "Если ты пользователь и хочешь найти ответ на вопрос, введи команду /find_answer."
    )
    await update.message.reply_text(text=help_message)

async def settings(update: Update, context: CallbackContext):
    print("Я в хендлере настроек")
    if update.effective_chat.type != "private":
        return
    keyboard = [
        [InlineKeyboardButton("Привязать чат для активации функций", callback_data='bind_chat')],
        [InlineKeyboardButton("Настроить чат", callback_data='configure_chat')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет! Я ваш бот-помощник для чатов!\n\n'
        'Вы выбрали режим редактирования и привязки чатов. Выберете действие: \n',
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
    context.user_data['text_for_spam'] = update.message.text

    if chat_type in ["group", "supergroup"]:
        if is_suspicious(chat_id, text):
            await forward_suspicious_message(context.bot, chat_id, message_id, chat_name, timestamp)

    else:
        action = context.user_data.get('action')

        if action == 'add':
            await add_admins(update, context)
        elif action == 'remove':
            await remove_admins(update, context)
        elif 'action' in context.user_data and context.user_data['action'] in ['add_spam', 'delete_spam']:
            context.user_data['text_for_spam'] = text
            await process_spam_keywords(update, context)
        elif action in ['add_faq_question', 'add_faq_answer', 'delete_faq_question']:
            await handle_faq_text(update, context)
        else:
            # Если действие не установлено, не обрабатываем текст
            await update.message.reply_text("Пожалуйста, выберите действие из меню.")