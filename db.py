import os
from dotenv import load_dotenv

from peewee import (
    PostgresqlDatabase,
    Model,
    TextField,
    ForeignKeyField,
)

from pgvector.peewee import VectorField
from pgvector.psycopg2 import register_vector

# =========================
# LOAD .env
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)

DB_NAME = os.getenv("POSTGRES_DB_NAME")
HOST = os.getenv("POSTGRES_DB_HOST")
PORT = os.getenv("POSTGRES_DB_PORT")
USER = os.getenv("POSTGRES_DB_USER")
PASSWORD = os.getenv("POSTGRES_DB_PASSWORD") or ""

# =========================
# DB CONNECTION
# =========================
db = PostgresqlDatabase(
    DB_NAME,
    host=HOST,
    port=int(PORT),
    user=USER,
    password=PASSWORD
)

# =========================
# BASE MODEL
# =========================
class BaseModel(Model):
    class Meta:
        database = db


# =========================
# TABLES
# =========================
class Documents(BaseModel):
    name = TextField()

    class Meta:
        db_table = "documents"


class Tags(BaseModel):
    name = TextField(unique=True)

    class Meta:
        db_table = "tags"


class DocumentTags(BaseModel):
    document_id = ForeignKeyField(Documents, on_delete="CASCADE")
    tag_id = ForeignKeyField(Tags, on_delete="CASCADE")

    class Meta:
        db_table = "document_tags"


class DocumentInformationChunks(BaseModel):
    document_id = ForeignKeyField(Documents, on_delete="CASCADE")
    chunk = TextField()
    embedding = VectorField()   # SAFE

    class Meta:
        db_table = "document_information_chunks"


# =========================
# DB HELPERS
# =========================
def connect_db():
    if db.is_closed():
        db.connect()

        # ✅ SAFE VECTOR REGISTRATION
        try:
            register_vector(db.connection)
        except Exception:
            pass


def create_tables():
    db.create_tables([
        Documents,
        Tags,
        DocumentTags,
        DocumentInformationChunks
    ])


# AUTO CONNECT
connect_db()