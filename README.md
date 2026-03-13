# Mail Registry MVP

MVP-система учета входящей и исходящей электронной корреспонденции для инфраструктуры iRedMail + Nextcloud + OnlyOffice.

## Что реализовано в этом репозитории

- Базовый FastAPI backend.
- SQLAlchemy-модели для справочников, реестра, вложений, счетчиков, аудита.
- API реестра:
  - список и фильтрация;
  - создание записи с проверкой дублей (`message_id`/`message_hash` в рамках `mailbox_id`);
  - изменение статуса и ответственного;
  - экспорт в `.xlsx`.
- Сервис нумерации в формате `<COMPANY>-ВХ/ИСХ-YYYY-XXXXXX`.
- Заглушки IMAP collector / Nextcloud WebDAV клиента / polling worker.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Проверка:

- `GET /health`
- `GET /docs`

## Структура

```text
app/
  api/          # REST-роуты
  core/         # конфигурация
  db/           # база и сессии
  models/       # SQLAlchemy модели
  repositories/ # доступ к данным
  schemas/      # Pydantic схемы
  services/     # доменные сервисы
  tasks/        # фоновые задачи
```

## Дальнейшие шаги (для полного MVP)

1. Подключить Alembic миграции.
2. Реализовать IMAP-парсер письма и загрузку `.eml`/вложений в Nextcloud через WebDAV.
3. Добавить UI-реестр (Jinja2+HTMX или React).
4. Включить RBAC по ролям (администратор/оператор/руководитель/исполнитель).
5. Добавить планировщик (APScheduler/Celery) для цикла опроса каждые 5 минут.
