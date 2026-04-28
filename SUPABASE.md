# Supabase PostgreSQL

1. В Supabase откройте Project Settings -> Database -> Connection string.
2. Скопируйте URI connection string и замените `[YOUR-PASSWORD]` на пароль базы.
3. Создайте `.env` рядом с `main.py`:

```env
SUPABASE_DATABASE_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
JWT_SECRET_KEY=<long-random-secret>
ADMIN_EMAIL=admin@cifrograd.ru
ADMIN_PASSWORD=<admin-password>
CORS_ORIGINS=http://localhost:5173
```

Можно использовать и `DATABASE_URL`, но `SUPABASE_DATABASE_URL` имеет приоритет.
Если в строке Supabase нет `sslmode=require`, приложение добавит его автоматически.

После настройки примените миграции:

```bash
.venv/bin/alembic upgrade head
```

Если хотите создать таблицы через Supabase SQL Editor или Supabase CLI, используйте SQL-миграцию:

```text
supabase/migrations/20260428000000_initial_academy_tables.sql
```

Запуск API:

```bash
.venv/bin/uvicorn main:app --reload
```
