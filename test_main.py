def test_get_document_not_found(client):
    response = client.get("/documents/9999")

    assert response.status_code == 404

def test_create_and_get_document(client):
    document = {
        "title": "Test document",
        "filename": "test.txt",
        "user": "tester",
        "data": "2026-10-02"
    }

    response = client.post("/documents", json=document)

    assert response.status_code == 201

    created_document = response.json()
    document_id = created_document["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200

    received_document = response.json()

    assert received_document["id"] == document_id
    assert received_document["title"] == "Test document"
    assert received_document["filename"] == "test.txt"
    assert received_document["user"] == "tester"
    assert received_document["data"] == "2026-10-02"


def test_create_document_invalid_data(client):
    document = {
        "title": "a",
        "filename": "x",
        "user": "ab",
        "data": "2026-10-02"
    }

    response = client.post("/documents", json=document)

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert len(errors) == 3

    error_fields = [error["loc"][-1] for error in errors]

    assert "title" in error_fields
    assert "filename" in error_fields
    assert "user" in error_fields

def test_update_document(client, created_document):
    document_id = created_document["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"title": "New title"}
    )

    assert response.status_code == 200

    updated_document = response.json()

    assert updated_document["id"] == document_id
    assert updated_document["title"] == "New title"
    assert updated_document["filename"] == "fixture.txt"
    assert updated_document["user"] == "tester"
    assert updated_document["data"] == "2026-10-02"


def test_delete_document(client, created_document):
    document_id = created_document["id"]

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted"}

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 404
def test_get_documents_with_fixture(client, created_documents):
    response = client.get("/documents?offset=0&limit=3")

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 3
    assert documents[0]["id"] == created_documents[0]["id"]
    assert documents[1]["id"] == created_documents[1]["id"]
    assert documents[2]["id"] == created_documents[2]["id"]
def test_admin_endpoint_requires_authentication(client):
    response = client.get("/admin")

    assert response.status_code == 401
def test_user_cannot_access_admin(client, created_user):
    response = client.post(
        "/login",
        json={
            "username": "test_user",
            "password": "1234"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin access required"
    }
def test_admin_can_access_admin_endpoint(client, created_admin):
    response = client.post(
        "/login",
        json={
            "username": "test_admin",
            "password": "1234"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Hello admin",
        "username": "test_admin",
        "role": "admin"
    }