import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from peewee import SQL

from db import DocumentInformationChunks, db
from embedding import get_embedding

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# GROQ CLIENT (FIXED)
# =========================
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),   # ✅ FIXED
    base_url="https://api.groq.com/openai/v1"
)

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Chat With Documents")
st.title("📄 Chat With Documents")

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def push_message(msg):
    st.session_state["messages"].append(msg)


# =========================
# CHAT FUNCTION
# =========================
async def send_message(user_input: str):

    # 1. EMBEDDING
    query_vector = list(map(float, get_embedding(user_input)))

    # 2. VECTOR SEARCH (pgvector FIXED)
    with db.atomic():
        results = (
            DocumentInformationChunks
            .select()
            .order_by(SQL("embedding <-> %s::vector", (query_vector,)))
            .limit(5)
        )

        context = "\n".join([r.chunk for r in results])

    # 3. STORE USER MESSAGE
    push_message({
        "role": "user",
        "content": user_input,
        "references": [context]
    })

    # 4. PROMPT
    prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.

Context:
{context}

Question:
{user_input}
"""

    # 5. GROQ RESPONSE
    retries = 0

    while True:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",   # ✅ WORKING MODEL
                messages=[
                    {"role": "system", "content": "You are a helpful RAG assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.choices[0].message.content

            push_message({
                "role": "assistant",
                "content": answer,
                "references": None
            })

            break

        except Exception as e:
            retries += 1
            if retries > 5:
                raise e
            await asyncio.sleep(1)   # ✅ FIXED sleep

    st.rerun()


# =========================
# CHAT UI RENDER
# =========================
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg.get("references"):
            with st.expander("Context"):
                st.write(msg["references"][0])


# =========================
# INPUT BOX
# =========================
input_message = st.chat_input("Ask something from your documents")

if input_message:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_message(input_message))
    loop.close()