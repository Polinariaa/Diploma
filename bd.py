import sqlite3
import json

# Подключение к базе данных (или её создание, если она не существует)
conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

# Создание таблицы
c.execute('''CREATE TABLE IF NOT EXISTS chats
             (chat_id INTEGER PRIMARY KEY, name TEXT, is_bot_active BOOLEAN, admins TEXT)''')

# Добавление записи
def add_chat(chat_id, name, is_bot_active, admins):
    c.execute("INSERT INTO chats (chat_id, name, is_bot_active, admins) VALUES (?, ?, ?, ?)",
              (chat_id, name, is_bot_active, json.dumps(admins)))
    conn.commit()

# Запрос данных
def get_chat(chat_id):
    c.execute("SELECT * FROM chats WHERE chat_id=?", (chat_id,))
    return c.fetchone()

# Обновление данных
def set_bot_active(chat_id, is_active):
    c.execute("UPDATE chats SET is_bot_active=? WHERE chat_id=?", (is_active, chat_id))
    conn.commit()

# Переносите логику взаимодействия с данными из внутреннего словаря в эти функции