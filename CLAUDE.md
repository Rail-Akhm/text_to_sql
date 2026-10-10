# Text-to-SQL — Corporate MVP

## Project Overview
Корпоративный инструмент для преобразования естественного языка в SQL-запросы.
Цель — MVP: задаёшь вопрос на русском/английском, получаешь SQL и контекст релевантных полей.

## Environments

| | Домашняя машина | Рабочая машина |
|---|---|---|
| LLM | OpenRouter — `stepfun/step-3.5-flash:free` | LiteLLM proxy — `qwen3:latest` |
| Embeddings | OpenRouter — `baai/bge-m3` | LiteLLM proxy — `qwen3-embedding:latest` |
| LLM endpoint | `https://openrouter.ai/api/v1` | `https://spb99akl-dgx02.gazprom-neft.local/v1` |
| Database | PostgreSQL 16 (Docker, локально) | Greenplum (`edw`) |
| Каталог данных | `edm.data_catalog` (~90 полей) | `prj_brddwh.edm_embedded` (~282+ полей) |
| SSL | — | `verify=False` (корп. сертификат) |
| Конфиг | `.env` | захардкожен в `work/` (gitignored) |

## Tech Stack

| Слой | Технология |
|------|-----------|
| UI | Streamlit (локально) |
| Backend | Python |
| Vector storage | Обычные таблицы (`FLOAT8[]` / `_numeric`, без pgvector) |
| Similarity | numpy cosine similarity (Python) |

## Architecture

```
User (Streamlit)
     ↓
get_embedding(question) → модель эмбеддингов
     ↓
cosine_similarity() → Top-10 полей из каталога данных
     ↓
expand_to_full_tables()
  ├── все поля найденных таблиц
  └── FK-парсинг описаний "(tablename.id)" → подтягивает связанные таблицы
     ↓
build_schema_context() → текстовая схема релевантных таблиц (формат schema.table)
     ↓
generate_sql(question, schema_context) → LLM
     ↓
st.code(sql, language="sql") + st.expander(найденные таблицы + поля со score)
```

## Project Structure

```
text_to_sql/
├── CLAUDE.md
├── README.md
├── .env                        # реальные секреты, в gitignore
├── .env.example                # шаблон для новых разработчиков
├── .gitignore                  # credentials/, .env, work/
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
├── streamlit/
│   └── app.py                  # Streamlit: text-to-SQL (домашняя машина)
└── work/                       # рабочая машина — НЕ в git (gitignored, содержит credentials)
    ├── app.py                  # Streamlit: text-to-SQL (Greenplum + локальный LLM)
    ├── app_stub.py             # заглушка для проверки Streamlit
    ├── vectorize_catalog.py    # векторизация каталога через LiteLLM proxy
    └── scalability.md          # план масштабирования при росте каталога и пользователей
```

## Run Commands

```bash
# Зависимости
pip install -r requirements.txt

# --- Домашняя машина ---
# Поднять БД
cd docker && docker-compose up -d && cd ..
# Первоначальная настройка (DDL + данные + векторизация)
python setup.py
# Запустить UI
streamlit run streamlit/app.py

# --- Рабочая машина ---
# Векторизация каталога (запускать при добавлении новых ЭД)
python work/vectorize_catalog.py
# Запустить UI
streamlit run work/app.py
```

## Setup Script (setup.py)
Выполняет три шага по порядку:
1. Применяет `postgres/init.sql` и `postgres/init_edm.sql` к БД
2. Запускает `postgres/seed_data.py` — 1000 строк в каждую из 10 таблиц
3. Запускает `embeddings/vectorize_catalog.py` — векторизует ~90 записей каталога

## Key Decisions
- Векторы хранятся в `FLOAT8[]` / `_numeric` в обычных таблицах (без pgvector)
- Cosine similarity считается в Python через numpy (каталог ~300 строк, быстро)
- Каталог кешируется через `@st.cache_resource` — грузится один раз при старте
- Top-10 релевантных полей → expand_to_full_tables → LLM получает полную схему найденных таблиц
- FK-автоматика: если описание поля содержит `(tablename.id)`, связанная таблица добавляется в контекст автоматически
- SQL генерируется в формате `schema.table` (актуально для Greenplum с несколькими схемами)
- LLM генерирует только SELECT-запросы
- Пользователю показывается SQL + раскрывающийся блок с найденными таблицами и полями со score
- MVP: без авторизации, без мультитенантности
- Коммиты только по явному запросу пользователя
- Папка `work/` в gitignore — содержит захардкоженные credentials рабочей среды

## Scalability
При росте каталога свыше 10k ЭД или числа пользователей — см. `work/scalability.md`.
Краткий план: numpy-матрица (до 50k) → FAISS (до 500k) → pgvector в Greenplum (500k+).

## Home Environment Variables

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

## Domain Tables (домашняя машина, схема public)

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

## Work Catalog Tables (рабочая машина, БД edw)

| Таблица | Описание |
|---------|---------|
| `prj_brddwh.edm_embedded` | Каталог ЭД: object_schema, object_name, column_name, ent_name, embedding |
