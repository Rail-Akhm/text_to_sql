import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)
MODEL = os.getenv("OPENROUTER_MODEL")

st.set_page_config(page_title="Text-to-SQL", page_icon="🗄️", layout="centered")
st.title("Text-to-SQL")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Задайте вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            completion = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
            )
            response = completion.choices[0].message.content

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
