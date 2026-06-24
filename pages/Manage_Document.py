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

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Manage Documents")
st.title("📄 Manage Documents")

IDEAL_CHUNK_LENGTH = 4000


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        return "\n\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    except Exception as e:
        st.error(f"PDF reading failed: {e}")
        return ""


# =========================
# DELETE DOCUMENT
# =========================
def delete_document(document_id: int):
    try:
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

        st.success("Document deleted successfully")

    except Exception as e:
        st.error(f"Delete failed: {e}")


# =========================
# UPLOAD DOCUMENT
# =========================
def upload_document(name: str, pdf_bytes: bytes):

    existing = Documents.select().where(
        Documents.name == name
    ).first()

    if existing:
        st.warning("Document already exists")
        return

    text = extract_pdf_text(pdf_bytes)

    if not text.strip():
        st.error("No text found in PDF")
        return

    chunks = [
        text[i:i + IDEAL_CHUNK_LENGTH]
        for i in range(0, len(text), IDEAL_CHUNK_LENGTH)
        if text[i:i + IDEAL_CHUNK_LENGTH].strip()
    ]

    try:
        with db.atomic():

            doc_id = Documents.create(name=name)

            data = []

            progress = st.progress(0)

            for i, chunk in enumerate(chunks):

                embedding = get_embedding(chunk)

                data.append(
                    {
                        "document_id": doc_id.id,
                        "chunk": chunk,
                        "embedding": embedding
                    }
                )

                progress.progress((i + 1) / len(chunks))

            DocumentInformationChunks.insert_many(data).execute()

            # attach first tag if available
            tag = Tags.select().first()

            if tag:
                DocumentTags.create(
                    document_id=doc_id,
                    tag_id=tag.id
                )

        st.success(
            f"Uploaded {name} ({len(chunks)} chunks)"
        )

    except Exception as e:
        st.error(f"Upload failed: {e}")


# =========================
# UPLOAD UI
# =========================
file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if file and st.button("Upload"):

    upload_document(
        file.name,
        file.getvalue()
    )

    st.rerun()


# =========================
# DOCUMENT LIST
# =========================
documents = (
    Documents
    .select(
        Documents.id,
        Documents.name,
        fn.array_agg(Tags.name).alias("tags")
    )
    .join(
        DocumentTags,
        JOIN.LEFT_OUTER,
        on=(Documents.id == DocumentTags.document_id)
    )
    .join(
        Tags,
        JOIN.LEFT_OUTER,
        on=(DocumentTags.tag_id == Tags.id)
    )
    .group_by(Documents.id)
)


# =========================
# DISPLAY DOCUMENTS
# =========================
if documents.exists():

    for doc in documents:

        box = st.container(border=True)

        box.write(f"📄 {doc.name}")

        if doc.tags:
            valid_tags = [t for t in doc.tags if t]

            if valid_tags:
                box.write(
                    f"🏷️ {', '.join(valid_tags)}"
                )

        if box.button(
            "🗑 Delete",
            key=f"delete_{doc.id}"
        ):
            delete_document(doc.id)
            st.rerun()

else:
    st.info("No documents found")