<h1 align="center">Roll Call Bot</h1>

<p align="center">
  Telegram-бот для проведения переклички учебной группы
</p>

---

## О проекте

`roll-call-bot` автоматизирует перекличку в Telegram:

- администратор запускает перекличку и указывает название пары;
- бот рассылает участникам кнопки отметки присутствия;
- администратор получает сводный отчет и может обновлять его в один клик.

---

## Используемые технологии

<img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img alt="aiogram" src="https://img.shields.io/badge/aiogram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" />
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
<img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
<img alt="asyncpg" src="https://img.shields.io/badge/asyncpg-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />

---

## Конфигурация

Конфигурация читается из `data.json`:

```json
{
  "bot_token": "<TELEGRAM_BOT_TOKEN>",
  "admin_id": 123456789,
  "database": {
    "admin": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
    "db_name": "roll-call-bot"
  }
}
```

### Структура БД

Для работы бот получает данные из таблицы `users`:

```sql
CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  name TEXT NOT NULL
);
```

Поля:
- `user_id` - Telegram ID пользователя.
- `name` - имя пользователя.

---

## Запуск

Из папки проекта
```bash
python main.py
```

---

## Использование

1. Админ отправляет `/start` боту.
2. Админ получает меню действий
3. Админ выбирает проведение переклички и вводит название пары
4. Участники отмечаются кнопками `Я есть` или `Меня нет`
5. Админ получает отчет переклички с возможностью обновления
