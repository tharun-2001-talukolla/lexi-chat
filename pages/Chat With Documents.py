import os
import time
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
# CHECK API KEY
# =========================
if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is missing.")
    st.stop()

# =========================
# GROQ CLIENT
# =========================
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
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
    st.session_state.messages = []


def push_message(role, content, references=None):
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "references": references
        }
    )


# =========================
# CHAT FUNCTION
# =========================
def send_message(user_input: str):

    try:
        # Generate embedding
        query_vector = list(map(float, get_embedding(user_input)))

        # Vector search
        with db.atomic():
            results = (
                DocumentInformationChunks
                .select()
                .order_by(
                    SQL(
                        "embedding <-> %s::vector",
                        (query_vector,)
                    )
                )
                .limit(5)
            )

            chunks = [row.chunk for row in results]

        if not chunks:
            push_message("user", user_input)
            push_message(
                "assistant",
                "No relevant documents found."
            )
            return

        context = "\n\n".join(chunks)

        # Store user message
        push_message(
            "user",
            user_input,
            references=context
        )

        prompt = f"""
You are a document-based assistant.

Rules:
- Answer ONLY from the provided context.
- If the answer is not present, say:
"I don't know based on the provided documents."
- Do not hallucinate.

Context:
{context}

Question:
{user_input}
"""

        retries = 0

        while retries < 5:
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful RAG assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                answer = response.choices[0].message.content

                push_message(
                    "assistant",
                    answer
                )

                break

            except Exception as e:
                retries += 1

                if retries == 5:
                    st.error(f"Error: {str(e)}")
                    return

                time.sleep(1)

    except Exception as e:
        st.error(f"Error: {str(e)}")


# =========================
# DISPLAY CHAT HISTORY
# =========================
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg.get("references"):
            with st.expander("Retrieved Context"):
                st.text(msg["references"][:3000])


# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input(
    "Ask something from your documents"
)

if user_input:
    send_message(user_input)
    st.rerun()