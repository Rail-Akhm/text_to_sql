# Text-to-SQL — Corporate MVP

## Project Overview
Корпоративный инструмент для преобразования естественного языка в SQL-запросы.
Цель — MVP: задаёшь вопрос на русском/английском, получаешь SQL и контекст релевантных полей.

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
get_embedding(question) → baai/bge-m3 via OpenRouter
     ↓
cosine_similarity() → Top-10 из edm.data_catalog
     ↓
build_schema_context() → текстовая схема релевантных таблиц
     ↓
generate_sql(question, schema_context) → stepfun/step-3.5-flash via OpenRouter
     ↓
st.code(sql, language="sql") + st.expander(релевантные поля)
```

## Databases

| БД | Назначение |
|----|-----------|
| `postgres` | Схема `edm` — каталог данных с векторами (`edm.data_catalog`) + 10 рабочих таблиц |

> Все таблицы находятся в одной БД `postgres`. DATABASE_URL указывает на неё.

## Key Decisions
- Векторы хранятся в `FLOAT8[]` в обычных таблицах PostgreSQL (без pgvector)
- Cosine similarity считается в Python через numpy (каталог ~90 строк, быстро)
- Каталог `edm.data_catalog` кешируется через `@st.cache_resource` — грузится один раз при старте
- Top-10 релевантных полей передаются в контекст LLM
- LLM генерирует только SELECT-запросы
- Пользователю показывается SQL + раскрывающийся блок с найденными полями и score
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
│   ├── init_edm.sql            # схема edm, таблица data_catalog + данные
│   └── seed_data.py            # генерация синтетических данных (1000 строк/таблица)
├── embeddings/
│   └── vectorize_catalog.py    # векторизация edm.data_catalog через OpenRouter
└── streamlit/
    └── app.py                  # Streamlit: text-to-SQL интерфейс
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
docker exec -i text_to_sql_db psql -U admin -d postgres -f /dev/stdin < postgres/init.sql
docker exec -i text_to_sql_db psql -U admin -d postgres -f /dev/stdin < postgres/init_edm.sql

# Наполнить синтетическими данными
python postgres/seed_data.py

# Векторизовать каталог
python embeddings/vectorize_catalog.py

# Запустить UI
streamlit run streamlit/app.py
```

## Domain Tables (в БД postgres, схема public)

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

## EDM Catalog (в БД postgres, схема edm)

| Таблица | Описание |
|---------|---------|
| `edm.data_catalog` | Каталог всех полей: schema, table, column, description, embedding (FLOAT8[]) |
