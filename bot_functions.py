from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_chat, set_bot_active, get_user_admin_chats, get_admins_for_chat, get_active_user_admin_chats, \
    get_all_active_chats, add_spam_keyword, delete_spam_keyword, get_spam_keywords, get_admins_with_usernames_for_chat
from telegram import Bot
from manage_bot_admins import fetch_and_store_chat_members

async def handle_button(update: Update, context: CallbackContext):
    print("Я в хендлере кнопок")
    query = update.callback_query
    await query.answer()

    # Проверяем, является ли чат приватным
    if query.message.chat.type != "private":
        return  # Игнорируем запрос, если он не из личного чата

    user_id = query.from_user.id
    if query.data == 'bind_chat':
        admin_chats = get_user_admin_chats(user_id)
        valid_chats = []
        if admin_chats:
            for chat in admin_chats:
                if 'chat_id' in chat and await is_bot_admin(context.bot, chat['chat_id']):
                    valid_chats.append(chat)
        if valid_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"select_chat_{chat['chat_id']}")]
                for chat in valid_chats
            ]
            keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_to_main_settings")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Мы нашли чаты, в которых вы являетесь администратором. Какой из них вы хотите привязать к боту?",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("<< Назад", callback_data="back_to_main_settings")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="К сожалению, не нашли чат, к которому можно привязать бота\n\n"
                     "Чтобы привязать бота к чату, нужно:\n"
                     "1. Добавить бота в чат\n"
                     "2. Назначить бот администратором\n\n"
                     "Возможно, вы уже привязали бота к чату и можно переходить к его настройке. Если нет, то проследуйте инструкциям и вернитесь к привязке бота через основное меню.",
                reply_markup=reply_markup
            )
    elif query.data == 'configure_chat':
        admin_chats = get_active_user_admin_chats(user_id)
        if admin_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"config_chat_{chat_id}")]
                for chat_id, chat in admin_chats.items()
            ]
            keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_to_main_settings")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Вот все каналы, в которых вы являетесь администратором. Нажмите на нужный, чтобы увидеть параметры настройки.",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("<< Назад", callback_data="back_to_main_settings")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="К сожалению, у вас нет привязанных чатов, в которых вы являетесь администратором.",
                reply_markup=reply_markup
            )
    elif "select_chat_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        chat = get_chat(chat_id)
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data="bind_chat")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if chat:
            admins = get_admins_for_chat(chat_id)
            if user_id in admins:
                if set_bot_active(chat_id, True):
                    await query.edit_message_text(
                        text=f"Чат {chat['name']} успешно привязан. Бот активирован и готов к работе.",
                        reply_markup=reply_markup
                    )
                else:
                    await query.edit_message_text(text="Не удалось активировать бота для этого чата.",
                                                  reply_markup=reply_markup)
            else:
                await query.edit_message_text(text="Вы не являетесь администратором этого чата.",
                                              reply_markup=reply_markup)
        else:
            await query.edit_message_text(
                text="Не удалось найти чат в вашем списке или вы не являетесь его администратором.",
                reply_markup=reply_markup)
    elif "config_chat_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        chat = get_chat(chat_id)
        if chat:
            keyboard = [
                [InlineKeyboardButton("Редактировать список администраторов бота", callback_data=f"edit_admins_{chat_id}")],
                [InlineKeyboardButton("Редактировать спам-словарь", callback_data=f"edit_spam_{chat_id}")],
                [InlineKeyboardButton("<< Назад", callback_data="configure_chat")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"Вы выбрали чат '{chat['name']}'. Выберите действие:",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("<< Назад", callback_data="configure_chat")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Не удалось найти выбранный чат.",
                                          reply_markup=reply_markup)
    elif "edit_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        keyboard = [
            [InlineKeyboardButton("Добавить администраторов", callback_data=f"add_admins_{chat_id}")],
            [InlineKeyboardButton("Удалить администраторов", callback_data=f"remove_admins_{chat_id}")],
            [InlineKeyboardButton("Посмотреть список всех текущих администраторов",
                                  callback_data=f"view_admins_{chat_id}")],
            [InlineKeyboardButton("<< Назад", callback_data=f"config_chat_{chat_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите действие для редактирования списка администраторов.",
            reply_markup=reply_markup
        )
    elif "add_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        await fetch_and_store_chat_members(context.bot, chat_id)
        context.user_data['action'] = 'add'
        context.user_data['admin_action'] = {'chat_id': chat_id, 'action': 'add'}
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data=f"edit_admins_{chat_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Введите логин пользователя, которого хотите добавить в администраторы.\n"
                 "Только администратор чата может быть назначен на роль администратора бота.\n"
                 "Вы можете указать несколько логинов, разделив их пробелом.",
            reply_markup=reply_markup
        )
    elif "remove_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        context.user_data['action'] = 'remove'
        context.user_data['admin_action'] = {'chat_id': chat_id, 'action': 'remove'}
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data=f"edit_admins_{chat_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Введите логин пользователя, которого хотите удалить из администраторов.\n"
                 "Вы можете указать несколько логинов, разделив их пробелом.",
            reply_markup=reply_markup
        )
    elif "view_admins_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        chat = get_chat(chat_id)
        admins = get_admins_with_usernames_for_chat(chat_id)
        admin_list = "\n".join([f"@{admin}" for admin in admins]) if admins else "Администраторы не найдены."
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data=f"edit_admins_{chat_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Список администраторов для чата '{chat['name']}':\n{admin_list}",
            reply_markup=reply_markup
        )
    elif query.data == 'find_answer':
        all_chats = get_all_active_chats()  # функция, возвращающая все активные чаты из базы
        user_chats = []
        for chat in all_chats:
            if await is_user_member_of_chat(context.bot, chat['chat_id'], user_id):
                user_chats.append(chat)

        if user_chats:
            keyboard = [
                [InlineKeyboardButton(chat['name'], callback_data=f"answer_chat_{chat['chat_id']}")]
                for chat in user_chats
            ]
            keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_to_main_answer_find")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Вот все чаты с ботом, в которых вы состоите.\n"
                     "Выберете, в каком именно чате вы хотите найти ответ на вопрос",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("<< Назад", callback_data="back_to_main_answer_find")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Похоже, вы не состоите ни в одном чате с активированным ботом.",
                reply_markup=reply_markup
            )
    elif query.data.startswith('answer_chat_'):
        chat_id = query.data.split('_')[-1]
        chat_name = [chat['name'] for chat in get_all_active_chats() if str(chat['chat_id']) == chat_id][0]
        context.user_data['search_chat_id'] = chat_id  # Сохраняем ID чата для последующего поиска
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data="find_answer")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Ищем ответ на вопрос в чате {chat_name}. Введите пожалуйста свой вопрос.",
            reply_markup=reply_markup
        )
    elif query.data == 'back_to_main_settings':
        # Возвращаем пользователя к основному меню
        keyboard = [
            [InlineKeyboardButton("Привязать чат", callback_data='bind_chat')],
            [InlineKeyboardButton("Настроить чат", callback_data='configure_chat')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Вы находитесь в режиме редактирования и привязки чатов. Выберете действие:",
            reply_markup=reply_markup
        )
    elif query.data == 'back_to_main_answer_find':
        # Возвращаем пользователя к основному меню
        keyboard = [
            [InlineKeyboardButton("Найти ответ на вопрос", callback_data='find_answer')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Вы находитесь в режиме поиска ответа. Выберете действие:",
            reply_markup=reply_markup
        )
    elif "edit_spam_" in query.data:
        chat_id = int(query.data.split("_")[-1])
        keyboard = [
            [InlineKeyboardButton("Добавить спам-слова", callback_data=f"add_spam_{chat_id}")],
            [InlineKeyboardButton("Удалить спам-слова", callback_data=f"delete_spam_{chat_id}")],
            [InlineKeyboardButton("Посмотреть текущий список спам слов", callback_data=f"view_spam_{chat_id}")],
            [InlineKeyboardButton("<< Назад", callback_data=f"config_chat_{chat_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите действие для редактирования списка подозрительных слов.",
            reply_markup=reply_markup
        )
    elif "add_spam_" in query.data:
        chat_id = int(query.data.split('_')[2])
        context.user_data['action'] = 'add_spam'
        context.user_data['spam_chat_id'] = chat_id  # сохраняем ID чата для действий со спам-словами
        await query.edit_message_text(
            text="Введите слова через запятую, которые вы хотите добавить:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_spam_{chat_id}")]])
        )
    elif "delete_spam_" in query.data:
        chat_id = int(query.data.split('_')[2])
        context.user_data['action'] = 'delete_spam'
        context.user_data['spam_chat_id'] = chat_id
        await query.edit_message_text(
            text="Введите слова через запятую, которые вы хотите удалить:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_spam_{chat_id}")]])
        )
    elif 'spam_action' in context.user_data:
        chat_id = context.user_data['spam_action']['chat_id']
        action = context.user_data['spam_action']['action']
        text = context.user_data.get('text_for_spam', '')
        keywords = [keyword.strip() for keyword in text.split(',')]
        if action == 'add':
            for keyword in keywords:
                add_spam_keyword(chat_id, keyword)
            message = "Слова добавлены в список подозрительных."
        elif action == 'delete':
            for keyword in keywords:
                delete_spam_keyword(chat_id, keyword)
            message = "Слова удалены из списка подозрительных."
        await update.message.reply_text(text=message)
    elif query.data.startswith('view_spam_'):
        chat_id = int(query.data.split('_')[2])
        spam_keywords = get_spam_keywords(chat_id)
        if spam_keywords:
            keywords_text = '\n'.join(spam_keywords)
            response_text = f"Текущий список спам-слов в чате:\n{keywords_text}"
        else:
            response_text = "Список спам-слов пуст."

        await query.edit_message_text(
            text=response_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("<< Назад", callback_data=f"edit_spam_{chat_id}")]
            ])
        )
    else:
        await query.edit_message_text(text="Произошла ошибка. Попробуйте снова.")

# Проверка на то, является ли бот администратором
async def is_bot_admin(bot: Bot, chat_id: int):
    try:
        chat_administrators = await bot.get_chat_administrators(chat_id)
        bot_user_id = bot.id
        for admin in chat_administrators:
            if admin.user.id == bot_user_id:
                return True
        return False
    except Exception as e:
        print(f"Error checking bot admin status: {str(e)}")
        return False

# Проверка на то, является ли конкретный пользователь пользователем чата
async def is_user_member_of_chat(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status not in ['left', 'kicked']
    except Exception as e:
        print(f"Error checking membership in chat {chat_id}: {str(e)}")
        return False