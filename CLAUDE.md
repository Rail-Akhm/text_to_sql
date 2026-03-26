# Text-to-SQL — Corporate MVP

## Project Overview
Корпоративный инструмент для преобразования естественного языка в SQL-запросы.
Цель — MVP: задаёшь вопрос на русском/английском, получаешь SQL и результат.

## Tech Stack

| Слой | Технология |
|------|-----------|
| UI | Streamlit (локально) |
| Backend | Python |
| LLM | OpenRouter — `stepfun/step-3.5-flash:free` |
| Embeddings | OpenRouter — `baai/bge-m3` |
| Database | PostgreSQL 16 (Docker, локально) |
| Vector storage | Обычные таблицы PostgreSQL (`FLOAT8[]`, без pgvector) |

## Architecture

```
User (Streamlit)
     ↓
Query Processor
     ↓
Embedding (baai/bge-m3 via OpenRouter) → Vector Search (edm.data_catalog)
     ↓
Schema Context Builder
     ↓
LLM (stepfun/step-3.5-flash via OpenRouter) → SQL Generation
     ↓
SQL Executor (PostgreSQL)
     ↓
Result Display (Streamlit)
```

## Databases

| БД | Назначение |
|----|-----------|
| `postgres` | Схема `edm` — каталог данных с векторами (`edm.data_catalog`) |
| `text_to_sql` | Рабочие таблицы нефтегазовой предметной области |

## Key Decisions
- Векторы хранятся в `FLOAT8[]` в обычных таблицах PostgreSQL (без pgvector)
- OpenRouter используется и для эмбеддингов, и для генерации SQL
- Каталог данных (`edm.data_catalog`) описывает все поля всех таблиц — используется для vector search и построения контекста
- Локальный запуск — без облачных зависимостей, кроме OpenRouter API
- MVP: без авторизации, без мультитенантности
- Коммиты только по явному запросу пользователя

## Project Structure

```
text_to_sql/
├── CLAUDE.md
├── README.md
├── .env                        # реальные секреты, в gitignore
├── .env.example                # шаблон для новых разработчиков
├── .gitignore                  # credentials/, .env
├── commands/
│   └── commit.md               # конвенция коммитов
├── docker/
│   └── docker-compose.yml      # PostgreSQL 16
├── postgres/
│   ├── init.sql                # DDL 10 нефтегазовых таблиц
│   └── init_edm.sql            # схема edm, таблица data_catalog + данные
├── embeddings/
│   └── vectorize_catalog.py    # векторизация edm.data_catalog через OpenRouter
└── streamlit/
    └── app.py                  # Streamlit чат-бот (подключён к OpenRouter LLM)
```

## Environment Variables

```
OPENROUTER_API_KEY=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
OPENROUTER_EMBEDDING_MODEL=baai/bge-m3

POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=text_to_sql
DATABASE_URL=postgresql://admin:password@localhost:5432/postgres
```

## Run Commands

```bash
# Поднять БД
cd docker && docker-compose up -d

# Применить DDL вручную
docker exec -i text_to_sql_db psql -U admin -d text_to_sql -f /dev/stdin < postgres/init.sql
docker exec -i text_to_sql_db psql -U admin -d postgres   -f /dev/stdin < postgres/init_edm.sql

# Векторизовать каталог
python embeddings/vectorize_catalog.py

# Запустить UI
streamlit run streamlit/app.py
```

## Domain Tables (postgres / public → text_to_sql)

| Таблица | Описание |
|---------|---------|
| `fields` | Месторождения |
| `formations` | Геологические пласты |
| `wells` | Скважины |
| `production` | Ежемесячная добыча (нефть, газ, вода) |
| `gas_reserves` | Запасы газа по категориям А/В/С |
| `repair_types` | Справочник видов ремонтов |
| `well_repairs` | Ремонты скважин (КРС, ПРС, ГРП) |
| `well_equipment` | Оборудование скважин (ЭЦН, ШГН) |
| `incidents` | Аварии и инциденты |
| `gtm` | Геолого-технические мероприятия |
