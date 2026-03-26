import os
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)
EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, table_name, column_name, description
        FROM edm.data_catalog
        WHERE embedding IS NULL AND description IS NOT NULL
    """)
    rows = cur.fetchall()

    if not rows:
        print("Все записи уже векторизованы.")
        return

    print(f"Найдено записей для векторизации: {len(rows)}")

    for row_id, table_name, column_name, description in rows:
        text = f"таблица {table_name}, поле {column_name}: {description}"
        embedding = get_embedding(text)

        cur.execute(
            "UPDATE edm.data_catalog SET embedding = %s WHERE id = %s",
            (embedding, row_id),
        )
        print(f"  ✓ {table_name}.{column_name}")

    conn.commit()
    cur.close()
    conn.close()
    print("Готово.")


if __name__ == "__main__":
    main()
