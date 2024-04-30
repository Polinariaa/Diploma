from database import get_admins_for_chat

async def forward_suspicious_message(bot, chat_id, message_id, chat_name, timestamp):
    admins = get_admins_for_chat(chat_id)  # Получаем список админов из базы
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    for admin in admins:
        try:
            await bot.forward_message(chat_id=admin, from_chat_id=chat_id, message_id=message_id)
            await bot.send_message(
                chat_id=admin,
                text=f"Подозрительное сообщение в чате {chat_name}.\nВремя отправки сообщения в чат: {time_str}"
            )
        except Exception as e:
            print(f"Не удалось переслать сообщение администратору {admin}: {str(e)}")

def is_suspicious(text):
    suspicious_keywords = ['spam', 'scam', 'hack']
    return any(keyword in text.lower() for keyword in suspicious_keywords)