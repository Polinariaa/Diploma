from telegram import Update
from telegram.ext import CallbackContext
from database import get_chat, find_message_in_chat


async def handle_search_query(update: Update, context: CallbackContext):
    chat_id = context.user_data.get('search_chat_id')
    if chat_id:
        user_question = update.message.text
        found_messages = find_message_in_chat(chat_id, user_question)
        if found_messages:
            for message in found_messages:
                await forward_message_to_user(update, context, message, chat_id)
        else:
            await update.message.reply_text("Сообщение с таким текстом не найдено.")
        context.user_data.pop('search_chat_id', None)  # Очищаем после использования
    else:
        await update.message.reply_text("Выберите чат для поиска из меню.")

async def forward_message_to_user(update, context, message, chat_id):
    # Получение информации о чате для указания в сообщении
    chat = get_chat(chat_id)
    chat_name = chat['name'] if chat else "неизвестный чат"

    try:
        # Пересылка сообщения
        await context.bot.forward_message(
            chat_id=update.effective_user.id,
            from_chat_id=chat_id,
            message_id=message['message_id']
        )
        # Отправка дополнительного уведомления
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Найденное сообщение из чата {chat_name}."
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при пересылке сообщения: {str(e)}")