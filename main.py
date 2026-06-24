import streamlit as st

st.set_page_config(page_title="Chat With Docs", layout="wide")

st.title("📄 Chat With Docs")
st.write("Welcome to your RAG-based Document Assistant")

st.markdown("""
## 🚀 Features
- Upload PDFs
- Extract AI-powered chunks
- Store embeddings in PostgreSQL (pgvector)
- Chat with your documents using Gemini
- Tag-based document filtering
""")
