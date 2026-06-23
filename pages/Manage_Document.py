import streamlit as st
from io import BytesIO
from pypdf import PdfReader

from peewee import JOIN, fn

from db import (
    Documents,
    DocumentTags,
    DocumentInformationChunks,
    Tags,
    db
)

from embedding import get_embedding

st.set_page_config(page_title="Manage Documents")
st.title("📄 Manage Documents")

IDEAL_CHUNK_LENGTH = 4000


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )


# =========================
# DELETE DOCUMENT
# =========================
def delete_document(document_id: int):
    with db.atomic():
        DocumentInformationChunks.delete().where(
            DocumentInformationChunks.document_id == document_id
        ).execute()

        DocumentTags.delete().where(
            DocumentTags.document_id == document_id
        ).execute()

        Documents.delete().where(
            Documents.id == document_id
        ).execute()

    st.success("Deleted successfully")


# =========================
# UPLOAD DOCUMENT
# =========================
def upload_document(name: str, pdf_bytes: bytes):

    text = extract_pdf_text(pdf_bytes)

    if not text.strip():
        st.error("No text found in PDF")
        return

    chunks = [
        text[i:i + IDEAL_CHUNK_LENGTH]
        for i in range(0, len(text), IDEAL_CHUNK_LENGTH)
    ]

    with db.atomic():

        doc_id = Documents.insert(name=name).execute()

        DocumentInformationChunks.insert_many([
            {
                "document_id": doc_id,
                "chunk": chunk,
                "embedding": get_embedding(chunk)
            }
            for chunk in chunks
        ]).execute()

        tag = Tags.select().first()

        if tag:
            DocumentTags.create(
                document_id=doc_id,
                tag_id=tag.id
            )

    st.success(f"Uploaded {name} ({len(chunks)} chunks)")


# =========================
# UI UPLOAD
# =========================
file = st.file_uploader("Upload PDF", type="pdf")

if file and st.button("Upload"):
    upload_document(file.name, file.getvalue())
    st.rerun()


# =========================
# SHOW DOCUMENTS (FIXED)
# =========================
documents = (
    Documents
    .select(
        Documents.id,
        Documents.name,
        fn.array_agg(Tags.name).alias("tags")
    )
    .join(DocumentTags, JOIN.LEFT_OUTER)
    .join(Tags, JOIN.LEFT_OUTER)
    .group_by(Documents.id)
)


if documents:
    for doc in documents:
        box = st.container(border=True)

        box.write(f"📄 {doc.name}")

        if doc.tags and doc.tags[0]:
            box.write(f"🏷️ {', '.join([t for t in doc.tags if t])}")

        # ✅ SAFE BUTTON (no lambda issue)
        if box.button("🗑 Delete", key=f"del_{doc.id}"):
            delete_document(doc.id)
            st.rerun()

else:
    st.info("No documents found")