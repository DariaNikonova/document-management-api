def test_get_document_not_found(client, auth_headers):
    response = client.get(
        "/documents/9999",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_and_get_document(client, auth_headers):
    response = client.post(
        "/documents",
        json={"title": "Test document", "filename": "test.txt"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    created_document = response.json()

    assert created_document["id"] is not None
    assert created_document["title"] == "Test document"
    assert created_document["filename"] == "test.txt"
    assert created_document["user"] == "test_user"
    assert created_document["data"] is not None

    document_id = created_document["id"]
    response = client.get(
        f"/documents/{document_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_create_document_invalid_data(client, auth_headers):
    response = client.post(
        "/documents",
        json={"title": "a", "filename": "x"},
        headers=auth_headers,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    error_fields = [error["loc"][-1] for error in errors]

    assert "title" in error_fields
    assert "filename" in error_fields


def test_update_document(client, auth_headers, created_document):
    document_id = created_document["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"title": "Updated title"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    updated_document = response.json()

    assert updated_document["title"] == "Updated title"
    assert updated_document["filename"] == "fixture.txt"
    assert updated_document["user"] == "test_user"


def test_delete_document(client, auth_headers, created_document):
    document_id = created_document["id"]

    response = client.delete(
        f"/documents/{document_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    response = client.get(
        f"/documents/{document_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_documents_with_fixture(
    client,
    auth_headers,
    created_documents,
):
    response = client.get(
        "/documents",
        params={"limit": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    received_documents = response.json()

    assert len(received_documents) == 3

    expected_ids = {document["id"] for document in created_documents}
    received_ids = {document["id"] for document in received_documents}

    assert received_ids == expected_ids


def test_user_sees_only_own_documents(
    client,
    auth_headers,
    admin_headers,
    created_document,
):
    response = client.post(
        "/documents",
        json={"title": "Admin document", "filename": "admin.txt"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text

    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200

    documents = response.json()
    assert len(documents) == 1
    assert documents[0]["user"] == "test_user"
    assert documents[0]["id"] == created_document["id"]


def test_user_cannot_access_another_users_document(
    client,
    auth_headers,
    admin_headers,
):
    response = client.post(
        "/documents",
        json={
            "title": "Private admin document",
            "filename": "private.txt",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text

    document_id = response.json()["id"]

    response = client.get(
        f"/documents/{document_id}",
        headers=auth_headers,
    )
    assert response.status_code == 403

    response = client.patch(
        f"/documents/{document_id}",
        json={"title": "Attempted change"},
        headers=auth_headers,
    )
    assert response.status_code == 403

    response = client.delete(
        f"/documents/{document_id}",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_admin_endpoint_requires_authentication(client):
    response = client.get("/admin")
    assert response.status_code == 401


def test_user_cannot_access_admin(client, auth_headers):
    response = client.get("/admin", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_access_admin_endpoint(client, admin_headers):
    response = client.get("/admin", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "test_admin"
    assert response.json()["role"] == "admin"

def test_invalid_token_returns_401(client):
    response = client.get(
        "/documents",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401

def test_token_with_non_numeric_sub_returns_401(client):
    import jwt
    import os

    secret_key = os.getenv("SECRET_KEY")

    token = jwt.encode(
        {
            "sub": "abc",
            "role": "user",
            "exp": 4102444800,
        },
        secret_key,
        algorithm="HS256",
    )

    response = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401

def test_expired_token_returns_401(client):
    import jwt
    import os
    from datetime import datetime, timedelta, timezone

    secret_key = os.getenv("SECRET_KEY")

    expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "exp": expired_time,
        },
        secret_key,
        algorithm="HS256",
    )

    response = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401

def test_token_without_sub_returns_401(client):
    import jwt
    import os

    secret_key = os.getenv("SECRET_KEY")

    token = jwt.encode(
        {
            "role": "user",
            "exp": 4102444800,
        },
        secret_key,
        algorithm="HS256",
    )

    response = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401

def test_user_cannot_see_another_users_documents(
    client,
    auth_headers,
    admin_headers,
):
    response = client.post(
        "/documents",
        json={
            "title": "Admin private document",
            "filename": "admin_private.txt",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201

    response = client.get(
        "/documents",
        headers=auth_headers,
    )
    assert response.status_code == 200

    documents = response.json()

    assert all(document["user"] == "test_user" for document in documents)
    assert all(
        document["title"] != "Admin private document"
        for document in documents
    )