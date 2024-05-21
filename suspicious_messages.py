from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_admins_for_chat, get_spam_keywords, add_spam_keyword, delete_spam_keyword

async def process_spam_keywords(update, context):
    action = context.user_data.get('action')
    chat_id = context.user_data.get('spam_chat_id')
    text = context.user_data.pop('text_for_spam', '')
    keywords = [keyword.strip() for keyword in text.split(',')]
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("<< Назад", callback_data=f"edit_spam_{chat_id}")]
    ])
    if action == 'add_spam':
        for keyword in keywords:
            add_spam_keyword(chat_id, keyword)
        await update.message.reply_text(
            text="Слова добавлены в список подозрительных.",
            reply_markup=reply_markup
        )
    elif action == 'delete_spam':
        for keyword in keywords:
            delete_spam_keyword(chat_id, keyword)
        await update.message.reply_text(
            text="Слова удалены из списка подозрительных.",
            reply_markup=reply_markup
        )

    # Очищаем данные после обработки
    context.user_data.pop('action', None)
    context.user_data.pop('spam_chat_id', None)

async def forward_suspicious_message(bot, chat_id, message_id, chat_name, timestamp):
    admins = get_admins_for_chat(chat_id)  # Получаем список админов из базы
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # Получаем информацию о чате
    chat = await bot.get_chat(chat_id)
    chat_username = chat.username  # Получаем username чата

    if chat_username:
        message_link = f"https://t.me/{chat_username}/{message_id}"
    else:
        message_link = "Чат является приватным, ссылка недоступна."
    for admin in admins:
        try:
            await bot.forward_message(chat_id=admin, from_chat_id=chat_id, message_id=message_id)
            await bot.send_message(
                chat_id=admin,
                text=f"Подозрительное сообщение в чате {chat_name}.\n"
                     f"Время отправки сообщения в чат: {time_str}\n\n"
                     f"Ссылка на сообщение: {message_link}"
            )
        except Exception as e:
            print(f"Не удалось переслать сообщение администратору {admin}: {str(e)}")

def is_suspicious(chat_id, text):
    suspicious_keywords = get_spam_keywords(chat_id)
    return any(keyword in text.lower() for keyword in suspicious_keywords)