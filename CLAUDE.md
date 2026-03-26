# Text-to-SQL — Corporate MVP

## Project Overview
Корпоративный инструмент для преобразования естественного языка в SQL-запросы.
Цель — MVP: задаёшь вопрос на русском/английском, получаешь SQL и результат.

## Tech Stack

| Слой | Технология |
|------|-----------|
| UI | Streamlit (локально) |
| Backend | Python |
| LLM / Embeddings | OpenRouter API |
| Database | PostgreSQL (локально) |
| Vector storage | Обычные таблицы PostgreSQL (векторов мало, pgvector не нужен) |

## Architecture

```
User (Streamlit)
     ↓
Query Processor
     ↓
Embedding (OpenRouter) → Vector Search (PostgreSQL table)
     ↓
Schema Context Builder
     ↓
LLM (OpenRouter) → SQL Generation
     ↓
SQL Executor (PostgreSQL)
     ↓
Result Display (Streamlit)
```

## Key Decisions
- Векторы хранятся в обычных таблицах PostgreSQL (cosine similarity вручную или через функцию)
- OpenRouter используется и для эмбеддингов, и для генерации SQL
- Локальный запуск — без облачных зависимостей, кроме OpenRouter API
- MVP: без авторизации, без мультитенантности

## Project Structure (planned)
```
text_to_sql/
├── CLAUDE.md
├── .env                  # OPENROUTER_API_KEY, DATABASE_URL
├── requirements.txt
├── app.py                # Streamlit entry point
├── src/
│   ├── embeddings.py     # OpenRouter embedding calls
│   ├── vector_store.py   # PostgreSQL vector search
│   ├── schema_loader.py  # Load DB schema into context
│   ├── sql_generator.py  # LLM → SQL via OpenRouter
│   └── db.py             # PostgreSQL connection & query execution
└── sql/
    └── init.sql          # Schema for vector store tables
```

## Environment Variables
```
OPENROUTER_API_KEY=...
DATABASE_URL=postgresql://user:password@localhost:5432/text_to_sql
```

## Development Rules
- Не усложнять: MVP, минимум абстракций
- Все конфиги — через `.env` (python-dotenv)
- Streamlit запускается через `streamlit run app.py`
- PostgreSQL поднимается локально (Docker или нативно)
- Коммиты только по явному запросу пользователя
