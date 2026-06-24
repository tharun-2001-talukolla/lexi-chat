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
PORT = int(os.getenv("POSTGRES_DB_PORT", 5432))
USER = os.getenv("POSTGRES_DB_USER")
PASSWORD = os.getenv("POSTGRES_DB_PASSWORD", "")

# =========================
# DATABASE CONNECTION
# =========================
db = PostgresqlDatabase(
    DB_NAME,
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    sslmode="require"
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
    document_id = ForeignKeyField(
        Documents,
        backref="document_tags",
        on_delete="CASCADE"
    )

    tag_id = ForeignKeyField(
        Tags,
        backref="tag_documents",
        on_delete="CASCADE"
    )

    class Meta:
        db_table = "document_tags"


class DocumentInformationChunks(BaseModel):
    document_id = ForeignKeyField(
        Documents,
        backref="chunks",
        on_delete="CASCADE"
    )

    chunk = TextField()
    embedding = VectorField()

    class Meta:
        db_table = "document_information_chunks"


# =========================
# CONNECT DATABASE
# =========================
def connect_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)

        try:
            register_vector(db.connection())
        except Exception as e:
            print("Vector registration warning:", e)


# =========================
# CREATE TABLES
# =========================
def create_tables():
    connect_db()

    db.create_tables(
        [
            Documents,
            Tags,
            DocumentTags,
            DocumentInformationChunks
        ],
        safe=True
    )


# =========================
# AUTO CONNECT
# =========================
connect_db()


# =========================
# CREATE TABLES MANUALLY
# =========================
if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")