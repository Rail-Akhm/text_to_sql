"""
Скрипт первоначальной настройки проекта.
Запускать один раз после клонирования репозитория.

Порядок действий:
  1. Применяет DDL (init.sql, init_edm.sql) к БД postgres
  2. Наполняет таблицы синтетическими данными
  3. Векторизует каталог данных

Запуск: python setup.py
"""
import os
import subprocess
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def step(msg: str):
    print(f"\n{'─' * 50}")
    print(f"  {msg}")
    print(f"{'─' * 50}")


def apply_sql(filepath: str):
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    cur.execute(sql)
    cur.close()
    conn.close()
    print(f"  ✓ {os.path.basename(filepath)}")


def run_script(filepath: str):
    result = subprocess.run(
        [sys.executable, filepath],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  ✗ Ошибка при выполнении {filepath}")
        sys.exit(1)


def main():
    print("\n=== Text-to-SQL: первоначальная настройка ===")

    # 1. DDL
    step("1/3 Применяем DDL...")
    apply_sql(os.path.join(BASE_DIR, "postgres", "init.sql"))
    apply_sql(os.path.join(BASE_DIR, "postgres", "init_edm.sql"))

    # 2. Синтетические данные
    step("2/3 Наполняем таблицы синтетическими данными...")
    run_script(os.path.join(BASE_DIR, "postgres", "seed_data.py"))

    # 3. Векторизация каталога
    step("3/3 Векторизуем каталог данных...")
    run_script(os.path.join(BASE_DIR, "embeddings", "vectorize_catalog.py"))

    print("\n=== Готово! Запустите интерфейс: ===")
    print("  streamlit run streamlit/app.py\n")


if __name__ == "__main__":
    main()
