# Room Reservation (FastAPI, Async)

Мини‑сервис для бронирования переговорных комнат: аутентификация пользователей (JWT), управление комнатами, создание/редактирование бронирований, проверки пересечений и прав доступа. Асинхронный стек (FastAPI + SQLAlchemy 2.x + SQLite/aiosqlite).

## Стек
- **Python** 3.12
- **FastAPI** 0.111
- **Starlette lifespan** (вместо `@app.on_event`)
- **Pydantic** v2 / **pydantic-settings** v2
- **SQLAlchemy** 2.x (async) + **SQLite** (aiosqlite)
- **FastAPI Users** 14.x (JWT аутентификация)
- **Alembic** (миграции)

## Структура проекта
```
app/
  api/
    endpoints/
      meeting_room.py
      reservation.py
    routers.py
    validators.py
  core/
    base.py
    config.py
    db.py
    init_db.py        # создание первого суперпользователя (lifespan)
    user.py           # интеграция fastapi-users
  crud/
    base.py
    meeting_room.py
    reservation.py
  models/
    meeting_room.py
    reservation.py
    user.py
alembic/              # миграции
```
> Структура соответствует скриншоту из репозитория.

## Быстрый старт

### 1) Окружение
```bash
python -m venv venv
source venv/bin/activate               # Windows: venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt        # если файла нет — см. раздел "Зависимости"
```
> Если установлен Anaconda, **деактивируйте `base`** (`conda deactivate`), иначе `uvicorn --reload` может стартовать не из venv.

### 2) Переменные окружения
Создайте **.env** в корне проекта:
```
APP_TITLE=Бронирование переговорок
DESCRIPTION=API для бронирования переговорных
# Используйте АБСОЛЮТНЫЙ путь к файлу БД!
DATABASE_URL=sqlite+aiosqlite:////Users/<you>/Dev_new/room_reservation/fastapi.db
SECRET=supersecretjwt
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```
- Для **приложения** требуется именно SQLAlchemy‑URL как выше.
- Для **DBeaver** нужен путь к файлу БД **без** префикса `sqlite+aiosqlite:///`.

### 3) Миграции БД
```bash
alembic upgrade head
```

### 4) Запуск dev-сервера
```bash
python -m uvicorn app.main:app --reload
```
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

При старте (через **lifespan**) выполняется `create_first_superuser()` — создаётся суперпользователь из `.env` (функция идемпотентная).

## Аутентификация и пользователи
Маршруты на базе **FastAPI Users**:
- `POST /auth/jwt/login` — логин (получение JWT)
- `POST /auth/register` — регистрация
- `GET /users/me` — профиль
- Админ‑ручки из базового роутера подключены, кроме удаления пользователя.

Роли:
- **Суперпользователь** — управление переговорками, просмотр всех бронирований.
- **Обычный пользователь** — свои бронирования.

## Эндпоинты

### Meeting Rooms
Только суперпользователь может создавать/обновлять/удалять комнаты.
- `POST /meeting_rooms/` — создать
- `GET /meeting_rooms/` — список
- `PATCH /meeting_rooms/{id}` — частичное обновление
- `DELETE /meeting_rooms/{id}` — удалить
Валидации: уникальность `name` и существование комнаты.

**Пример:**
```http
POST /meeting_rooms/
Authorization: Bearer <JWT>
{
  "name": "Большой зал",
  "description": "Проектор + экран"
}
```

### Reservations
- `POST /reservations/` — создать
- `GET /reservations/` — все (только суперюзер)
- `GET /reservations/my_reservations` — мои
- `PATCH /reservations/{id}` — обновить
- `DELETE /reservations/{id}` — удалить

Ключевые проверки:
- `from_reserve < to_reserve` (модельный валидатор Pydantic v2, mode="after")
- `from_reserve` позже «сейчас» (UTC, aware datetime)
- отсутствие пересечений бронирований для одной комнаты
- существование комнаты
- права: редактировать/удалять может владелец или суперюзер

**Пример:**
```http
POST /reservations/
Authorization: Bearer <JWT>
{
  "meetingroom_id": 1,
  "from_reserve": "2025-08-12T09:00:00Z",
  "to_reserve":   "2025-08-12T10:00:00Z",
}
```

## Настройки (pydantic-settings v2)
- Используйте `model_config = SettingsConfigDict(...)` вместо `class Config`.
- `EmailStr` импортируется из `pydantic`, а не из `pydantic_settings`.
- Рекомендуется хранить дату/время в UTC и сравнивать с `datetime.now(timezone.utc)`.


