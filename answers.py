from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_faq, delete_faq, get_all_faqs, get_all_active_chats, get_context
from utils import is_user_member_of_chat
import openai


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
            [InlineKeyboardButton(chat['name'], callback_data=f"select_answer_chat_{chat['chat_id']}")]
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

    keyboard = [[InlineKeyboardButton("<< Назад", callback_data=f"select_answer_chat_{chat_id}")]]
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

async def handle_search_query(chat_id, question):
    print(chat_id)
    context_text = get_context(chat_id)
    if not context_text:
        context_text = "Контекст не установлен для этого чата."
    print(context_text)
    client = openai.OpenAI(
        base_url="url",
        api_key="key"
    )
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "system",
          "content": context_text
        },
        {
          "role": "user",
          "content": question
        }
      ],
      temperature=0.7,
      max_tokens=1000,
      top_p=1
    )
    return response.choices[0].message.content


async def edit_context(update: Update, context: CallbackContext):
    print("Редактирование контекста...")
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    keyboard = [
        [InlineKeyboardButton("Редактировать контекст", callback_data=f"edit_text_context_{chat_id}")],
        [InlineKeyboardButton("Посмотреть текущий контекст", callback_data=f"view_context_{chat_id}")],
        [InlineKeyboardButton("<< Назад", callback_data=f"config_chat_{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Контекст - это то, что мы будем передавать в нейросеть для того, чтобы она могла дать ответ на " \
           f"вопросы, которые будут задавать пользователи. Чем более полный контекст, тем больше вопросов он " \
           f"сможет охватить и более точно на них ответить. " \
           f"Выберите действие:"
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def edit_context_text(update: Update, context: CallbackContext):
    print("Редактирование текста контекста...")
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    context.user_data['action'] = 'edit_text_context'
    context.user_data['context_chat_id'] = chat_id

    # Получение текущего контекста из базы данных
    current_context = get_context(chat_id)
    if current_context:
        text = f"Текущий контекст:\n\n{current_context}\n\nВведите новый контекст для чата:"
    else:
        text = "Введите новый контекст для чата:"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_context_{chat_id}")]])
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def view_context(update: Update, context: CallbackContext):
    print("Просмотр контекста...")
    query = update.callback_query
    chat_id = int(query.data.split("_")[-1])
    context_text = get_context(chat_id)
    if context_text:
        text = f"Текущий контекст:\n{context_text}"
    else:
        text = "Контекст не установлен."
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("<< Назад", callback_data=f"edit_context_{chat_id}")]])
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )