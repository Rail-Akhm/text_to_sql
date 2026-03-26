# Text-to-SQL

Корпоративный инструмент для преобразования вопросов на естественном языке в SQL-запросы.

## Стек

- **UI** — Streamlit
- **LLM / Embeddings** — OpenRouter
- **База данных** — PostgreSQL (локально)
- **Векторное хранилище** — обычные таблицы PostgreSQL

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Rail-Akhm/text_to_sql.git
cd text_to_sql
```

### 2. Установить зависимости

```bash
pip install openai python-dotenv streamlit
```

### 3. Настроить переменные окружения

```bash
cp .env.example .env
```

Заполнить `.env`:

```
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
```

### 4. Запустить

```bash
streamlit run streamlit/app.py
```

Открыть в браузере: [http://localhost:8501](http://localhost:8501)

## Структура проекта

```
text_to_sql/
├── .env.example        # Шаблон переменных окружения
├── .gitignore
├── CLAUDE.md           # Архитектура и решения по проекту
├── README.md
├── commands/
│   └── commit.md       # Конвенция коммитов
└── streamlit/
    └── app.py          # Streamlit приложение
```
