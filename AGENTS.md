# text_to_sql — рабочая память

## Что это
Корпоративный MVP text-to-SQL для нефтегазовой предметной области: вопрос на русском → векторный поиск релевантных полей каталога данных → LLM генерирует SELECT и показывает найденные таблицы со score.
Стек: Python + Streamlit (UI), PostgreSQL 16 в Docker (дома) / Greenplum `edw` (работа), эмбеддинги и LLM по OpenAI-совместимому API (OpenRouter дома, корпоративный LiteLLM proxy на работе). Векторы — обычные массивы `FLOAT8[]` / `_numeric`, без pgvector.
Пользователь один — автор проекта (Rail-Akhm), репозиторий `https://github.com/Rail-Akhm/text_to_sql`, ветка `master`.

## Состояние на 2026-10-10
- Проект живой, но заморожен в коде: последний коммит `6e30432 fix(ui): автоматическое расширение контекста через FK-парсинг` от 2026-03-26. После него коммитов нет.
- В рабочей копии есть НЕзакоммиченные изменения (проверено `git status` 2026-10-10): `.gitignore` (+ строка `work/`), `CLAUDE.md` (переписан в двуязычную таблицу «домашняя/рабочая машина»), `embeddings/vectorize_catalog.py`.
- Два окружения живут в одном репозитории: домашнее (`streamlit/app.py`, Postgres+OpenRouter) и рабочее (`work/`, Greenplum + LiteLLM proxy, папка в gitignore).
- Рабочее окружение расширено: каталог `prj_brddwh.edm_embedded` (~282+ поля) вместо `edm.data_catalog` (~90 полей); появились `work/app.py`, `work/app_stub.py`, `work/vectorize_catalog.py`, `work/scalability.md`.
- Тестов, CI, Makefile, pyproject.toml, Dockerfile и `.claude/settings.local.json` в проекте нет (проверено обходом дерева). Объём проекта ~76 КБ, 17 файлов без `.git`.

## Ключевые факты и грабли
- **Секреты в `work/`.** `work/app.py` и `work/vectorize_catalog.py` содержат захардкоженные credentials: API-ключ LiteLLM и пароль БД прямо в строке подключения (значения здесь намеренно не фиксируются). Файлы покрыты `.gitignore` (`work/`), в историю git не попадали — проверено `git ls-files work` и `git log --all -- work` (пусто). Строка `work/` в `.gitignore` добавлена, но ещё не закоммичена — не коммитить `work/` до этого.
- **Рассинхрон таблиц на рабочей машине.** `work/app.py` ЧИТАЕТ `prj_brddwh.edm_embedded`, а `work/vectorize_catalog.py` ПИШЕТ в `prj_brddwh.system_data_consumer_vec` (поля `dm_schema_name`, `code_business_system`, `domen`). Запуск векторизации «по CLAUDE.md» положит эмбеддинги не в ту таблицу, которую читает UI.
- **`DATABASE_URL` vs `POSTGRES_DB`.** В `.env.example` (и, вероятно, в `.env`) `DATABASE_URL` указывает на БД `postgres` (`/postgres`), а `POSTGRES_DB=text_to_sql`. `setup.py`, `seed_data.py`, `vectorize_catalog.py`, оба `app.py` используют только `DATABASE_URL`, поэтому DDL и данные уходят в БД `postgres`, хотя docker-compose создаёт `text_to_sql`.
- **Повторный `python setup.py` ломается.** `postgres/init.sql` использует `CREATE TABLE` без `IF NOT EXISTS` (в `init_edm.sql` `IF NOT EXISTS` есть только у схемы, таблица `edm.data_catalog` — без него). Второй запуск упадёт на шаге 1 «Применяем DDL». В `seed_data.py` нет `TRUNCATE`/`ON CONFLICT` — при удачном повторном прогоне данные продублируются.
- **Домашний `app.py` не знает про схемы.** `load_catalog()` в `streamlit/app.py` выбирает `table_name, column_name, description, embedding` без `schema_name` (хотя `edm.data_catalog` её хранит), и в контекст LLM идёт имя таблицы без схемы. На домашнем Postgres (одна схема `public`) это работает; для Greenplum с несколькими схемами схема учитывается только в `work/app.py`.
- **Векторный поиск — Python-цикл.** `vector_search()` вызывает `cosine_similarity()` на каждую строку каталога. По оценке из `work/scalability.md` это ~1–3 сек на 50k записей (на практике не замерялось). План развития: numpy-матрица до 50k → FAISS до 500k → pgvector (Greenplum поддерживает с GP7).
- **`httpx` не в requirements.** `requirements.txt` — только `openai`, `psycopg2-binary`, `python-dotenv`, `streamlit`, `numpy` (версии не зафиксированы). Рабочие скрипты `work/app.py` и `work/vectorize_catalog.py` импортируют `httpx` (приходит транзитивно с `openai`, но как явная зависимость рабочей машины не задекларирован).
- **Корпоративный TLS.** На работе OpenAI-клиент создаётся с `http_client=httpx.Client(verify=False)` из-за корпоративного сертификата; дома verify не отключается.
- **Кодировка.** `postgres/init*.sql`, `seed_data.py` и все скрипты — в UTF-8. Вывод в консоли PowerShell без смены кодировки показывает русский текст как mojibake (`РњРµСЃС‚РѕСЂРѕР¶РґРµРЅРёСЏ`) — это артефакт консоли, а не порча файлов. `setup.py` читает SQL с `encoding="utf-8"`.
- **FK-автоматика.** `expand_to_full_tables()` парсит описания вида `(tablename.id)` регуляркой `\((\w+)\.id\)` и дотягивает связанные таблицы в контекст — так решается проблема пропущенных JOIN-таблиц. Формат описаний в `init_edm.sql` этой регулярке соответствует.
- **Каталог кешируется один раз.** `@st.cache_resource` на `load_catalog()`: после добавления новых ЭД и векторизации нужен перезапуск Streamlit, иначе изменения не видны.
- **Пустой пароль-заглушка.** В `.env.example` и `CLAUDE.md` в `DATABASE_URL` стоит литерал `password` — это шаблон, не реальный секрет. Реальные значения только в `.env` (в git не попадал, проверено `git ls-files .env` — пусто).
- **Коммиты только по явному запросу** пользователя (зафиксировано в CLAUDE.md); конвенция — `commands/commit.md`: `<type>(<scope>): <описание>`, сообщение на русском, ≤72 символа, scope из `ui|db|embeddings|vector|schema|sql|config`.

## Как запускать и проверять
Домашняя машина (из корня `D:\projects\text_to_sql`):
```bash
pip install -r requirements.txt
cd docker && docker-compose up -d && cd ..   # postgres:16, контейнер text_to_sql_db, порт 5432, env_file ../.env, volume postgres_data
python setup.py                              # 1) init.sql + init_edm.sql  2) seed_data.py  3) embeddings/vectorize_catalog.py
streamlit run streamlit/app.py               # UI на http://localhost:8501
```
Рабочая машина (только на корпоративном контуре):
```bash
python work/vectorize_catalog.py             # запускать при добавлении новых ЭД (см. грабли про таблицу)
streamlit run work/app.py                    # UI с Greenplum + локальным LLM
streamlit run work/app_stub.py               # заглушка-чат без LLM и БД, для проверки, что Streamlit поднимается
```
Что проверять при правках: `streamlit run` + вопрос вида «добыча нефти по месторождениям за 2024 год» → SQL в блоке `st.code` и корректный список таблиц в expander «Релевантные таблицы и поля»; для `setup.py` — что шаг 3 печатает `✓ table.column` по каждой записи каталога. Автотестов нет, регрессии ловятся только ручным прогоном UI.

## Открытые вопросы
- Неизвестна фактическая размерность эмбеддингов (`qwen3-embedding:latest` и `baai/bge-m3`) — от неё зависит оценка памяти при 50k/500k ЭД в `work/scalability.md`; там же оставлен TODO: `print(len(get_embedding("тест")))`.
- Не выяснено, что считать источником истины на работе: `prj_brddwh.edm_embedded` или `prj_brddwh.system_data_consumer_vec` (см. рассинхрон).
- Не закоммичены изменения `.gitignore` / `CLAUDE.md` / `embeddings/vectorize_catalog.py`; нужно ли довести двуязычную документацию до коммита — не решено.
- Не реализован numpy-матричный `vector_search` (рекомендация №1 из `work/scalability.md`), хотя помечен как «30 минут работы, ускорение 50–100x».
- Судьба рабочего окружения вне корпоративной сети не проверялась: `work/app.py` жёстко завязан на `spb99akl-dgx02.gazprom-neft.local` и `spb99akl-adbm01.gazprom-neft.local`.

## Источники
- `CLAUDE.md` (прочитан целиком, 153 строки; версия из рабочей копии с незакоммиченными правками) — окружения, архитектура, структура, key decisions, список доменных таблиц.
- `README.md` (88 строк) — быстрый старт и описание пайплайна; в структуре проекта `work/` ещё не отражён.
- `C:\Users\raila\.claude\projects\D--projects-text-to-sql\memory\MEMORY.md` (22 строки) — предпочтения пользователя (коммиты по запросу, MVP-мышление, общение по-русски). Устаревшая часть: ссылается на несуществующие `src/embeddings.py`, `src/vector_store.py`, `src/sql_generator.py`, `src/db.py`, `sql/init.sql`, `app.py` в корне — этих файлов в проекте нет.
- `setup.py`, `requirements.txt`, `docker/docker-compose.yml`, `.gitignore`, `.env.example`, `commands/commit.md` — команды запуска, зависимости, порт 5432, конвенция коммитов.
- `streamlit/app.py`, `work/app.py`, `work/app_stub.py`, `embeddings/vectorize_catalog.py`, `work/vectorize_catalog.py` — фактическая логика и расхождение таблиц.
- `postgres/init.sql` (10 таблиц), `postgres/init_edm.sql` (схема `edm` + каталог ~90 полей), `postgres/seed_data.py` (seed(42), 1000 строк на таблицу) — схема данных и отсутствие идемпотентности.
- `work/scalability.md` (172 строки) — план масштабирования и оценки производительности.
- Проверки состояния: `git log --oneline -15`, `git status --short`, `git ls-files`, `git diff`, обход дерева проекта (2026-10-10). Файл `.env` (363 байта) не читался — только имена переменных через разбор строк.
