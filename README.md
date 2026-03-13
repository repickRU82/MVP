# Mail Registry MVP

MVP-система учета входящей и исходящей электронной корреспонденции для инфраструктуры iRedMail + Nextcloud + OnlyOffice.

## Реализовано

- FastAPI backend с API реестра и веб-интерфейсом на Jinja2.
- RBAC по ролям: `administrator`, `operator`, `manager`, `executor`.
- SQLAlchemy-модели и Alembic-миграции.
- IMAP collector + MIME parser: чтение `.eml`, извлечение метаданных и вложений.
- Nextcloud WebDAV клиент: создание папок и загрузка `original.eml`, `metadata.json`, вложений.
- APScheduler: цикл опроса ящиков каждые `POLL_INTERVAL_MINUTES`.
- Экспорт реестра в `.xlsx`.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m alembic upgrade head
uvicorn app.main:app --reload
```

## Доступ

- Swagger: `GET /docs`
- UI реестра: `GET /ui/registry?x_user_id=1&x_user_role=administrator`
- Health: `GET /health`

Для API доступов передавайте заголовки:

- `X-User-Id: 1`
- `X-User-Role: administrator`

## Миграции

```bash
python -m alembic revision --autogenerate -m "msg"
python -m alembic upgrade head
```

## Docker

```bash
docker compose up --build
```
