import os
import numpy as np
import psycopg2
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)
MODEL = os.getenv("OPENROUTER_MODEL")
EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL")
DATABASE_URL = os.getenv("DATABASE_URL")
TOP_K = 10


# ── вспомогательные функции ────────────────────────────────────────────────────

@st.cache_resource
def load_catalog():
    """Загружает каталог данных из edm.data_catalog один раз при старте."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, description, embedding
        FROM edm.data_catalog
        WHERE embedding IS NOT NULL
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def cosine_similarity(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def vector_search(query_embedding, catalog, top_k=TOP_K):
    scored = [
        (cosine_similarity(query_embedding, row[3]), row[0], row[1], row[2])
        for row in catalog
    ]
    scored.sort(reverse=True)
    return scored[:top_k]


def build_schema_context(relevant: list) -> str:
    tables: dict[str, list[str]] = {}
    for _, table_name, column_name, description in relevant:
        tables.setdefault(table_name, []).append(f"  - {column_name}: {description}")
    return "\n\n".join(
        f"Таблица `{t}`:\n" + "\n".join(cols) for t, cols in tables.items()
    )


def generate_sql(question: str, schema_context: str) -> str:
    system_prompt = f"""Ты SQL-эксперт корпоративной базы данных нефтегазовой компании (PostgreSQL).

Доступная схема (только эти таблицы и поля):
{schema_context}

Правила:
- Генерируй только SELECT-запросы
- Используй только таблицы и поля из схемы выше
- Возвращай только SQL-код, без пояснений и markdown
- Если запрос невозможно построить по схеме — напиши кратко почему
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


# ── UI ─────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Text-to-SQL", page_icon="🗄️", layout="centered")
st.title("Text-to-SQL")

catalog = load_catalog()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.code(msg["content"], language="sql")
        else:
            st.markdown(msg["content"])
        if "context" in msg:
            with st.expander("Релевантные поля из каталога"):
                for sim, table, col, desc in msg["context"]:
                    st.markdown(f"**{table}.{col}** `{sim:.3f}` — {desc}")

if prompt := st.chat_input("Задайте вопрос на русском..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ищу релевантные поля..."):
            query_embedding = get_embedding(prompt)
            relevant = vector_search(query_embedding, catalog)
            schema_context = build_schema_context(relevant)

        with st.spinner("Генерирую SQL..."):
            sql = generate_sql(prompt, schema_context)

        st.code(sql, language="sql")

        with st.expander("Релевантные поля из каталога"):
            for sim, table, col, desc in relevant:
                st.markdown(f"**{table}.{col}** `{sim:.3f}` — {desc}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": sql,
        "context": relevant,
    })
