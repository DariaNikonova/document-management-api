from datetime import date, datetime
import os

from sqlalchemy import create_engine, select, DateTime, func
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
)


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    filename: Mapped[str]
    user: Mapped[str]
    data: Mapped[date]
    description: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")


def create_document(
    db,
    document_title,
    document_filename,
    document_user,
):
    document = Document(
        title=document_title,
        filename=document_filename,
        user=document_user,
        data=date.today(),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document_by_id(db, document_id):
    query = select(Document).where(Document.id == document_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


def get_documents(db, offset, limit):
    query = select(Document).limit(limit).offset(offset)
    result = db.execute(query)
    return result.scalars().all()


def update_document(db, document_id, new_title):
    document = db.get(Document, document_id)

    if document is not None:
        document.title = new_title
        db.commit()
        db.refresh(document)
        return document


def delete_document(db, document_id):
    document = db.get(Document, document_id)

    if document is not None:
        db.delete(document)
        db.commit()