from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_faq, delete_faq, get_all_faqs, get_all_active_chats
from utils import is_user_member_of_chat


async def find_answer(update: Update, context: CallbackContext):
    print("Я в хендлере поиска ответа")

    if update.message:
        chat_type = update.effective_chat.type
        user_id = update.message.from_user.id
    elif update.callback_query:
        chat_type = update.callback_query.message.chat.type
        user_id = update.callback_query.from_user.id

    if chat_type != "private":
        return

    all_chats = get_all_active_chats()
    user_chats = [chat for chat in all_chats if await is_user_member_of_chat(context.bot, chat['chat_id'], user_id)]

    if user_chats:
        keyboard = [
            [InlineKeyboardButton(chat['name'], callback_data=f"view_faq_user_{chat['chat_id']}")]
            for chat in user_chats
        ]
        keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_to_main_answer_find")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(
                'Привет! Я ваш бот-помощник для чатов!\n\n'
                'Вы выбрали режим поиска ответов по чату. Выберите чат для просмотра FAQ:',
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.message.edit_text(
                'Привет! Я ваш бот-помощник для чатов!\n\n'
                'Вы выбрали режим поиска ответов по чату. Выберите чат для просмотра FAQ:',
                reply_markup=reply_markup
            )
    else:
        keyboard = [[InlineKeyboardButton("<< Назад", callback_data="back_to_main_answer_find")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text(
                text="Похоже, вы не состоите ни в одном чате с активированным ботом.",
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.message.edit_text(
                text="Похоже, вы не состоите ни в одном чате с активированным ботом.",
                reply_markup=reply_markup
            )

async def edit_faq(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    keyboard = [
        [InlineKeyboardButton("Добавить вопрос", callback_data=f"add_faq_question_{chat_id}")],
        [InlineKeyboardButton("Удалить вопрос", callback_data=f"delete_faq_question_{chat_id}")],
        [InlineKeyboardButton("Посмотреть вопросы и ответы", callback_data=f"view_faq_admin_{chat_id}")],
        [InlineKeyboardButton("<< Назад", callback_data=f"config_chat_{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Выберите действие для редактирования FAQ.",
        reply_markup=reply_markup
    )

async def add_faq_question_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    context.user_data['action'] = 'add_faq_question'
    context.user_data['faq_chat_id'] = chat_id
    await query.edit_message_text(
        text="Введите вопрос, который вы хотите добавить:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]])
    )

async def delete_faq_question_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    context.user_data['action'] = 'delete_faq_question'
    context.user_data['faq_chat_id'] = chat_id
    faqs = get_all_faqs(chat_id)
    if faqs:
        keyboard = [
            [InlineKeyboardButton(f"{faq['question']}", callback_data=f"confirm_delete_faq_{faq['id']}")]
            for faq in faqs
        ]
        keyboard.append([InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите вопрос для удаления:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text="Нет вопросов для удаления.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]])
        )


async def view_faq_admin(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    faqs = get_all_faqs(chat_id)

    if faqs:
        faq_text = "\n\n".join([f"Вопрос: {faq['question']}\nОтвет: {faq['answer']}" for faq in faqs])
    else:
        faq_text = "Нет сохраненных вопросов и ответов."

    keyboard = [[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Текущие вопросы и ответы:\n\n{faq_text}",
        reply_markup=reply_markup
    )


async def view_faq_user(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    faqs = get_all_faqs(chat_id)

    if faqs:
        faq_text = "\n\n".join([f"Вопрос: {faq['question']}\nОтвет: {faq['answer']}" for faq in faqs])
    else:
        faq_text = "Нет сохраненных вопросов и ответов."

    keyboard = [[InlineKeyboardButton("<< Назад", callback_data="find_answer")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Текущие вопросы и ответы:\n\n{faq_text}",
        reply_markup=reply_markup
    )

async def handle_faq_text(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    chat_id = context.user_data.get('faq_chat_id')

    if action == 'add_faq_question':
        question = update.message.text
        context.user_data['faq_question'] = question
        context.user_data['action'] = 'add_faq_answer'
        await update.message.reply_text(
            text="Введите ответ на добавленный вопрос:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]])
        )
    elif action == 'add_faq_answer':
        answer = update.message.text
        question = context.user_data.get('faq_question')
        add_faq(chat_id, question, answer)
        context.user_data.pop('action', None)
        context.user_data.pop('faq_chat_id', None)
        context.user_data.pop('faq_question', None)
        await update.message.reply_text(
            text="Вопрос и ответ успешно добавлены!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]])
        )
    elif action == 'delete_faq_question':
        faq_id = int(update.callback_query.data.split("_")[-1])
        delete_faq(faq_id)
        context.user_data.pop('action', None)
        context.user_data.pop('faq_chat_id', None)
        await update.callback_query.message.edit_text(
            text="Вопрос и ответ успешно удалены!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_faq_{chat_id}")]])
        )