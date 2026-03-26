# Text-to-SQL

Корпоративный инструмент для преобразования вопросов на естественном языке в SQL-запросы для нефтегазовой предметной области.

## Стек

| Слой | Технология |
|------|-----------|
| UI | Streamlit |
| LLM | OpenRouter — `stepfun/step-3.5-flash:free` |
| Embeddings | OpenRouter — `baai/bge-m3` |
| База данных | PostgreSQL 16 (Docker) |
| Векторное хранилище | Обычные таблицы PostgreSQL (`FLOAT8[]`) |

## Как это работает

1. Пользователь задаёт вопрос на русском языке
2. Вопрос векторизуется через `baai/bge-m3`
3. Cosine similarity поиск по каталогу данных `edm.data_catalog` → Top-10 релевантных полей
4. LLM получает схему релевантных таблиц и генерирует SQL
5. SQL и найденные поля отображаются в интерфейсе

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Rail-Akhm/text_to_sql.git
cd text_to_sql
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

```bash
cp .env.example .env
# Заполнить OPENROUTER_API_KEY
```

### 4. Поднять PostgreSQL

```bash
cd docker && docker-compose up -d && cd ..
```

### 5. Первоначальная настройка (DDL + данные + векторизация)

```bash
python setup.py
```

### 6. Запустить UI

```bash
streamlit run streamlit/app.py
```

Открыть в браузере: [http://localhost:8501](http://localhost:8501)

## Структура проекта

```
text_to_sql/
├── .env.example                # Шаблон переменных окружения
├── .gitignore
├── requirements.txt            # Python-зависимости
├── setup.py                    # Скрипт первоначальной настройки
├── CLAUDE.md                   # Архитектура и решения по проекту
├── README.md
├── commands/
│   └── commit.md               # Конвенция коммитов
├── docker/
│   └── docker-compose.yml      # PostgreSQL 16
├── embeddings/
│   └── vectorize_catalog.py    # Векторизация каталога через OpenRouter
├── postgres/
│   ├── init.sql                # DDL 10 нефтегазовых таблиц
│   ├── init_edm.sql            # Схема EDM + каталог данных
│   └── seed_data.py            # Генерация синтетических данных
└── streamlit/
    └── app.py                  # Text-to-SQL интерфейс
```
