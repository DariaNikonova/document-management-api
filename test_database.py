import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import (
    Base,
    create_document,
    get_document_by_id,
    get_documents,
    update_document,
    delete_document,
)


test_engine = create_engine("sqlite:///test_database.db")

TestSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture
def db():
    Base.metadata.create_all(test_engine)

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(test_engine)


def test_create_document(db):
    document = create_document(
        db,
        "Test document",
        "test.txt",
        "tester",
        date(2026, 10, 2)
    )

    assert document.id is not None
    assert document.title == "Test document"
    assert document.filename == "test.txt"
    assert document.user == "tester"
    assert document.data == date(2026, 10, 2)


def test_get_document_by_id(db):
    created = create_document(
        db,
        "Test document",
        "test.txt",
        "tester",
        date(2026, 10, 2)
    )

    document = get_document_by_id(db, created.id)

    assert document is not None
    assert document.id == created.id
    assert document.title == "Test document"


def test_get_documents(db):
    create_document(db, "Doc 1", "1.txt", "user1", date(2026, 10, 2))
    create_document(db, "Doc 2", "2.txt", "user2", date(2026, 10, 2))
    create_document(db, "Doc 3", "3.txt", "user3", date(2026, 10, 2))

    documents = get_documents(db, offset=0, limit=2)

    assert len(documents) == 2
    assert documents[0].title == "Doc 1"
    assert documents[1].title == "Doc 2"


def test_update_document(db):
    created = create_document(
        db,
        "Old title",
        "test.txt",
        "tester",
        date(2026, 10, 2)
    )

    updated = update_document(
        db,
        created.id,
        "New title"
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "New title"


def test_delete_document(db):
    created = create_document(
        db,
        "Test document",
        "test.txt",
        "tester",
        date(2026, 10, 2)
    )

    delete_document(db, created.id)

    document = get_document_by_id(db, created.id)

    assert document is None


def test_get_document_by_id_not_found(db):
    document = get_document_by_id(db, 9999)

    assert document is None


def test_update_document_not_found(db):
    document = update_document(
        db,
        9999,
        "New title"
    )

    assert document is None


def test_delete_document_not_found(db):
    result = delete_document(db, 9999)

    assert result is None


def test_get_documents_limit(client):
    for i in range(5):
        client.post(
            "/documents",
            json={
                "title": f"Document {i}",
                "filename": f"{i}.txt",
                "user": "tester",
                "data": "2026-10-02"
            }
        )

    response = client.get("/documents?offset=0&limit=3")

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 3


def test_get_documents_invalid_pagination(client):
    response = client.get("/documents?offset=-1&limit=3")
    assert response.status_code == 422

    response = client.get("/documents?offset=0&limit=0")
    assert response.status_code == 422

    response = client.get("/documents?offset=0&limit=11")
    assert response.status_code == 422