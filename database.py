import sqlite3
import json

# Подключение к базе данных (или её создание, если она не существует)
conn = sqlite3.connect('bot_database.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Создание таблицы
c.execute('''CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    is_bot_active BOOLEAN
);''')
c.execute('''
CREATE TABLE IF NOT EXISTS chat_admins (
    chat_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
);''')
c.execute('''
CREATE TABLE IF NOT EXISTS chat_users_admins (
    chat_id INTEGER,
    user_id INTEGER,
    username TEXT,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
);
''')

# Запрос данных
def get_chat(chat_id):
    c.execute("SELECT * FROM chats WHERE chat_id=?", (chat_id,))
    return c.fetchone()

# Обновление данных
def set_bot_active(chat_id, is_active):
    c.execute("UPDATE chats SET is_bot_active=? WHERE chat_id=?", (is_active, chat_id))
    if c.rowcount == 0:
        print("No rows updated")
    conn.commit()
    return c.rowcount > 0

# Добавление записи
def add_chat(chat_id, name, is_bot_active, admins):
    c.execute("INSERT INTO chats (chat_id, name, is_bot_active) VALUES (?, ?, ?)",
              (chat_id, name, is_bot_active))
    for admin in admins:
        c.execute("INSERT INTO chat_admins (chat_id, user_id) VALUES (?, ?)",
                  (chat_id, admin))
    conn.commit()
def delete_chat(chat_id):
    c.execute("DELETE FROM chat_admins WHERE chat_id=?", (chat_id,))
    c.execute("DELETE FROM chats WHERE chat_id=?", (chat_id,))
    conn.commit()

def get_user_admin_chats(user_id):
    query = """
        SELECT c.* FROM chats c 
        JOIN chat_admins ca ON c.chat_id = ca.chat_id 
        WHERE ca.user_id = ? AND c.is_bot_active = 0
        """
    c.execute(query, (user_id,))
    rows = c.fetchall()
    return [{'chat_id': row['chat_id'], 'name': row['name']} for row in rows]

def get_active_user_admin_chats(user_id):
    query = """
        SELECT c.* FROM chats c 
        JOIN chat_admins ca ON c.chat_id = ca.chat_id 
        WHERE ca.user_id = ? AND c.is_bot_active = 1
        """
    c.execute(query, (user_id,))
    rows = c.fetchall()
    return {row['chat_id']: dict(row) for row in rows}

def get_admins_for_chat(chat_id):
    c.execute("SELECT user_id FROM chat_admins WHERE chat_id = ?", (chat_id,))
    return [row['user_id'] for row in c.fetchall()]

def add_chat_admin(chat_id, user_id):
    c.execute("INSERT INTO chat_admins (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
    conn.commit()

def delete_chat_admin(chat_id, user_id):
    c.execute("DELETE FROM chat_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    conn.commit()

def add_user_to_chat(chat_id, user_id, username):
    c.execute("INSERT OR IGNORE INTO chat_users_admins (chat_id, user_id, username) VALUES (?, ?, ?)",
              (chat_id, user_id, username))
    conn.commit()

def get_user_admin_id_by_login(chat_id, login):
    c.execute("SELECT user_id FROM chat_users_admins WHERE chat_id = ? AND username = ?", (chat_id, login))
    result = c.fetchone()
    if result:
        return result['user_id']
    return None

def is_user_admin_member_of_chat(chat_id, user_id):
    c.execute("SELECT 1 FROM chat_users_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    return c.fetchone() is not None

def is_user_admin_of_chat(chat_id, user_id):
    c.execute("SELECT 1 FROM chat_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    return c.fetchone() is not None

def add_user_admin_to_chat_admins(chat_id, user_id, username):
    c.execute("INSERT OR IGNORE INTO chat_users_admins (chat_id, user_id, username) VALUES (?, ?, ?)",
              (chat_id, user_id, username))
    conn.commit()


def print_all_chats():
    c.execute("SELECT * FROM chats")
    all_chats = c.fetchall()
    for chat in all_chats:
        print(chat)
    if not all_chats:
        print("No chats found")