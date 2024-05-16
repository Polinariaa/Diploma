from telegram import Bot

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