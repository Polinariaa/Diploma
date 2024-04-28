from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_chat, set_bot_active, get_user_admin_chats, get_admins_for_chat, add_chat_admin, \
    get_user_admin_id_by_login, get_active_user_admin_chats, delete_chat_admin, is_user_admin_of_chat, add_user_admin_to_chat_admins, \
    is_user_admin_member_of_chat
from telegram import Bot


async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == 'bind_chat':
        # Фильтруем только те чаты, где пользователь является администратором
        admin_chats = get_user_admin_chats(user_id)
        valid_chats = []
        if admin_chats:
            for chat in admin_chats:
                if 'chat_id' in chat and await is_bot_admin(context.bot, chat['chat_id']):
                    valid_chats.append(chat)
        if valid_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"select_chat_{chat['chat_id']}")]
                for  chat in valid_chats
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Отлично, мы нашли чаты, в которых вы являетесь администратором. Какой из них вы хотите привязать к боту?",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                text="К сожалению, не нашли чат, в который вы бы добавили бота или он бы ещё не был привязан. Возможно, вы не назначили боту права администратора. Добавьте бота и вернитесь к его привязке через основное меню."
            )
    elif query.data == 'configure_chat':
        admin_chats = get_active_user_admin_chats(user_id)
        if admin_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"config_chat_{chat_id}")]
                for chat_id, chat in admin_chats.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Хорошо, вот все каналы, в которых ты являешься администратором. Нажми на нужный, чтобы увидеть параметры настройки.",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                text="К сожалению, у вас нет привязанных чатов, в которых вы являетесь администратором."
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
    elif "config_chat_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        chat = get_chat(chat_id)
        if chat:
            keyboard = [
                [InlineKeyboardButton("Добавить администраторов", callback_data=f"add_admins_{chat_id}")],
                [InlineKeyboardButton("Удалить администраторов", callback_data=f"remove_admins_{chat_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"Вы выбрали чат '{chat['name']}'. Выберите действие:",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(text="Не удалось найти выбранный чат.")
    elif "add_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        await fetch_and_store_chat_members(context.bot, chat_id)
        context.user_data['action'] = 'add'
        context.user_data['admin_action'] = {'chat_id': chat_id, 'action': 'add'}
        await query.edit_message_text(
            text="Введите логин пользователя, которого хотите добавить в администраторы. Важно понимать, что администратором может стать только тот, у кого есть права администратора канала. Вы можете указать несколько логинов, разделив их пробелом."
        )
    elif "remove_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        context.user_data['action'] = 'remove'
        context.user_data['admin_action'] = {'chat_id': chat_id, 'action': 'remove'}
        await query.edit_message_text(
            text="Введите логин пользователя, которого хотите удалить из администраторов. Вы можете указать несколько логинов, разделив их пробелом."
        )
    else:
        await query.edit_message_text(text="Произошла ошибка. Попробуйте снова.")


async def handle_text(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    if action == 'add':
        await add_admins(update, context)
    elif action == 'remove':
        await remove_admins(update, context)
    else:
        # Если действие не установлено, не обрабатываем текст
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")

async def add_admins(update: Update, context: CallbackContext):
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
            await update.message.reply_text(f"В чат {chat['name']} добавлены администраторы: {admins_str}")
        else:
            await update.message.reply_text("Никого не удалось добавить в администраторы.")
    else:
        await update.message.reply_text(text="Произошла ошибка. Попробуйте снова.")

async def remove_admins(update: Update, context: CallbackContext):
    if 'admin_action' in context.user_data and context.user_data['admin_action'].get('action') == 'remove':
        # отладка
        action_info = context.user_data['admin_action']
        print(f"Action info: {action_info}")
        # отладка
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
            await update.message.reply_text(f"Из чата {chat['name']} удалены администраторы: {admins_str}")
        else:
            await update.message.reply_text("Никого не удалось удалить из администраторов.")
    else:
        print("No admin_action in context.user_data")
        await update.message.reply_text(text="Произошла ошибка. Попробуйте снова.")

async def fetch_and_store_chat_members(bot: Bot, chat_id: int):
    # Сначала получаем список администраторов чата
    chat_administrators = await bot.get_chat_administrators(chat_id)
    # Теперь сохраняем информацию о каждом администраторе в базу данных
    for admin in chat_administrators:
        # Добавьте проверку, чтобы не добавлять бота самого в список
        if not admin.user.is_bot:
            add_user_admin_to_chat_admins(chat_id, admin.user.id, admin.user.username or admin.user.first_name)

async def is_bot_admin(bot: Bot, chat_id: int):
    try:
        chat_administrators = await bot.get_chat_administrators(chat_id)
        bot_user_id = bot.id  # Получаем ID бота
        for admin in chat_administrators:
            if admin.user.id == bot_user_id:
                return True
        return False
    except Exception as e:
        print(f"Error checking bot admin status: {str(e)}")
        return False