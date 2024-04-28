from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_chat, set_bot_active, get_user_admin_chats, get_admins_for_chat

async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == 'bind_chat':
        # Фильтруем только те чаты, где пользователь является администратором
        admin_chats = get_user_admin_chats(user_id)

        if admin_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"select_chat_{chat_id}")]
                for chat_id, chat in admin_chats.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Отлично, мы нашли чаты, в которых вы являетесь администратором. Какой из них вы хотите привязать к боту?",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                text="К сожалению, не нашли чат, в который вы бы добавили бота или он бы ещё не был привязан. Добавьте бота и вернитесь к его привязке через основное меню."
            )
    elif "select_chat_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        #print(f"Received chat_id: {chat_id}")  # Логируем полученный chat_id
        #print(f"User ID: {user_id}")  # Логируем ID пользователя
        #print(f"chats_data for user: {chats_data.get(user_id)}")  # Логируем данные о чатах текущего пользователя
        chat = get_chat(chat_id)
        if chat:
            admins = get_admins_for_chat(chat_id)
            if user_id in admins:
                if set_bot_active(chat_id, True):
                    await query.edit_message_text(
                        text=f"Чат {chat['name']} успешно привязан. Бот активирован и готов к работе."
                    )
                else:
                    await query.edit_message_text(text="Не удалось активировать бота для этого чата.")
            else:
                await query.edit_message_text(text="Вы не являетесь администратором этого чата.")
        else:
            await query.edit_message_text(
                text="Не удалось найти чат в вашем списке или вы не являетесь его администратором.")
    else:
        await query.edit_message_text(text="Произошла ошибка. Попробуйте снова.")