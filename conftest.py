import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from test_database import TestSessionLocal, test_engine
from auth import hash_password
from database import User

@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(test_engine)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)

@pytest.fixture
def created_user(client):
    db = TestSessionLocal()

    user = User(
        username="test_user",
        hashed_password=hash_password("1234"),
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return user
@pytest.fixture
def created_admin(client):
    db = TestSessionLocal()

    user = User(
        username="test_admin",
        hashed_password=hash_password("1234"),
        role="admin"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return user

@pytest.fixture
def created_document(client):
    document = {
        "title": "Fixture document",
        "filename": "fixture.txt",
        "user": "tester",
        "data": "2026-10-02"
    }
    response = client.post("/documents", json=document)

    assert response.status_code == 201

    return response.json()
@pytest.fixture
def created_documents(client):
    documents = []

    for i in range(3):
        response = client.post(
            "/documents",
            json={
                "title": f"Document {i}",
                "filename": f"{i}.txt",
                "user": "tester",
                "data": "2026-10-02"
            }
        )

        assert response.status_code == 201
        documents.append(response.json())

    return documents