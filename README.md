# Telegram-бот: Chat-helper. Дипломный проект

Этот проект представляет собой бот на Python с различными функциями, такими как обработка подозрительных сообщений, управление администраторами бота и предоставление пользователям FAQ по запросу. Ниже приведено описание структуры проекта и руководства по использованию.

```Diploma/
├── .git/
├── .gitignore
├── __pycache__/
├── answers.py
├── bot_database.db
├── bot_functions.py
├── bot_init.py
├── database.py
├── main.py
├── manage_bot_admins.py
├── README.md
├── suspicious_messages.py
├── utils.py
├── venv/
```

- ```.git/```: Каталог Git, содержащий данные управления версиями.
- ```.gitignore```: Указывает файлы и каталоги, которые следует игнорировать Git.
- ```pycache/```: Каталог, содержащий скомпилированные файлы Python.
- ```answers.py```: Содержит функционал для обработки ответов.
- ```bot_database.db```: База данных SQLite для хранения данных бота.
- ```bot_functions.py```: Реализует основные функции бота.
- ```bot_init.py```: Скрипт инициализации бота.
- ```database.py```: Обрабатывает взаимодействие с базой данных.
- ```main.py```: Точка входа в приложение бота.
- ```manage_bot_admins.py```: Скрипт для управления администраторами бота.
- ```README.md```: Этот файл.
- ```suspicious_messages.py```: Обрабатывает обнаружение и обработку подозрительных сообщений.
- ```utils.py```: Вспомогательные функции, используемые в проекте.
- ```venv/```: Каталог виртуального окружения, содержащий зависимости.

## Запуск бота
Чтобы запустить бота, выполните скрипт main.py:
```commandline
python main.py
```