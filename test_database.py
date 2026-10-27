from datetime import date

import pytest
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
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_create_document(db):
    document = create_document(
        db, "Test document", "test.txt", "tester"
    )

    assert document.id is not None
    assert document.title == "Test document"
    assert document.filename == "test.txt"
    assert document.user == "tester"
    assert document.data == date.today()


def test_get_document_by_id(db):
    created = create_document(
        db, "Test document", "test.txt", "tester"
    )

    document = get_document_by_id(db, created.id)

    assert document is not None
    assert document.id == created.id
    assert document.title == "Test document"


def test_get_documents(db):
    create_document(db, "Doc 1", "1.txt", "user1")
    create_document(db, "Doc 2", "2.txt", "user2")
    create_document(db, "Doc 3", "3.txt", "user1")

    documents = get_documents(
        db,
        user="user1",
        offset=0,
        limit=1,
    )

    assert len(documents) == 1
    assert documents[0].title == "Doc 1"
    assert documents[0].user == "user1"

    next_page = get_documents(
        db,
        user="user1",
        offset=1,
        limit=1,
    )

    assert len(next_page) == 1
    assert next_page[0].title == "Doc 3"


def test_get_documents_returns_only_owner_documents(db):
    create_document(db, "User 1 document", "1.txt", "user1")
    create_document(db, "User 2 document", "2.txt", "user2")

    documents = get_documents(
        db,
        user="user1",
        offset=0,
        limit=10,
    )

    assert len(documents) == 1
    assert all(document.user == "user1" for document in documents)


def test_update_document(db):
    created = create_document(
        db, "Old title", "test.txt", "tester"
    )

    updated = update_document(db, created.id, "New title")

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "New title"
    assert updated.filename == "test.txt"
    assert updated.user == "tester"


def test_delete_document(db):
    created = create_document(
        db, "Test document", "test.txt", "tester"
    )

    delete_document(db, created.id)

    assert get_document_by_id(db, created.id) is None


def test_get_document_by_id_not_found(db):
    assert get_document_by_id(db, 9999) is None


def test_update_document_not_found(db):
    assert update_document(db, 9999, "New title") is None


def test_delete_document_not_found(db):
    assert delete_document(db, 9999) is None