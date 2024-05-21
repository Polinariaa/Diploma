from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Bot

from database import get_chat, add_chat_admin, get_user_admin_id_by_login, delete_chat_admin, is_user_admin_of_chat, \
    add_user_admin_to_chat_admins, is_user_admin_member_of_chat


# Добавление админов бота
async def add_admins(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("<< Назад", callback_data="configure_chat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if 'admin_action' in context.user_data and context.user_data['admin_action'].get('action') == 'add':
        chat_id = context.user_data['admin_action']['chat_id']
        chat = get_chat(chat_id)
        user_logins = update.message.text.split()
        added_admins = []
        for login in user_logins:
            user_id = get_user_admin_id_by_login(chat_id, login)
            print(f"Checking login: {login}, found user_id: {user_id}")
            if user_id and is_user_admin_member_of_chat(chat_id, user_id) and not is_user_admin_of_chat(chat_id, user_id):
                add_chat_admin(chat_id, user_id)
                added_admins.append(login)
        if added_admins:
            admins_str = ", ".join(added_admins)
            await update.message.reply_text(text=f"В чат {chat['name']} добавлены администраторы: {admins_str}",
                                            reply_markup=reply_markup)
        else:
            await update.message.reply_text(text="Никого не удалось добавить в администраторы.",
                                            reply_markup=reply_markup)
    else:
        await update.message.reply_text(text="Произошла ошибка. Попробуйте снова.",
                                        reply_markup=reply_markup)

# Удаление админов бота
async def remove_admins(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("<< Назад", callback_data="configure_chat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if 'admin_action' in context.user_data and context.user_data['admin_action'].get('action') == 'remove':
        chat_id = context.user_data['admin_action']['chat_id']
        chat = get_chat(chat_id)
        user_logins = update.message.text.split()
        removed_admins = []
        for login in user_logins:
            user_id = get_user_admin_id_by_login(chat_id, login)
            if user_id and is_user_admin_of_chat(chat_id, user_id):
                delete_chat_admin(chat_id, user_id)
                removed_admins.append(login)
        if removed_admins:
            admins_str = ", ".join(removed_admins)
            await update.message.reply_text(text=f"Из чата {chat['name']} удалены администраторы: {admins_str}",
                                            reply_markup=reply_markup)
        else:
            await update.message.reply_text(text="Никого не удалось удалить из администраторов.",
                                            reply_markup=reply_markup)
    else:
        print("No admin_action in context.user_data")
        await update.message.reply_text(text="Произошла ошибка. Попробуйте снова.",
                                        reply_markup=reply_markup)

# Обновление списка администраторов чата
async def fetch_and_store_chat_members(bot: Bot, chat_id: int):
    # Сначала получаем список администраторов чата
    chat_administrators = await bot.get_chat_administrators(chat_id)
    # Теперь сохраняем информацию о каждом администраторе в базу данных
    for admin in chat_administrators:
        if not admin.user.is_bot:
            add_user_admin_to_chat_admins(chat_id, admin.user.id, admin.user.username or admin.user.first_name)