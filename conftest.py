import pytest
from fastapi.testclient import TestClient

from main import app
from database import Base, User, get_db
from test_database import TestSessionLocal, test_engine
from auth import hash_password

@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def created_user(client):
    db = TestSessionLocal()
    try:
        user = User(
            username="test_user",
            hashed_password=hash_password("1234"),
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def created_admin(client):
    db = TestSessionLocal()
    try:
        admin = User(
            username="test_admin",
            hashed_password=hash_password("1234"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    finally:
        db.close()


@pytest.fixture
def auth_headers(client, created_user):
    response = client.post(
        "/login",
        json={"username": "test_user", "password": "1234"},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, created_admin):
    response = client.post(
        "/login",
        json={"username": "test_admin", "password": "1234"},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_document(client, auth_headers):
    response = client.post(
        "/documents",
        json={
            "title": "Fixture document",
            "filename": "fixture.txt",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def created_documents(client, auth_headers):
    documents = []

    for i in range(3):
        response = client.post(
            "/documents",
            json={
                "title": f"Document {i + 1}",
                "filename": f"document_{i + 1}.txt",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        documents.append(response.json())

    return documents