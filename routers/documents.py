from fastapi import HTTPException, Query, status, APIRouter, Depends

from schemas.documents import Document, DocumentCreate, DocumentUpdate
from database import (
    get_db,
    get_document_by_id,
    create_document as create_document_db,
    get_documents as get_documents_db,
    delete_document as delete_document_db,
    update_document as update_document_db,
)
from auth import get_current_user

documents_router = APIRouter()


@documents_router.post(
    "/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=Document,
)
def create_document(
    document: DocumentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_document_db(
        db,
        document.title,
        document.filename,
        current_user.username,
    )


@documents_router.get(
    "/documents",
    response_model=list[Document],
)
def get_documents(
    db=Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=10),
    current_user=Depends(get_current_user),
):
    return get_documents_db(
        db,
        current_user.username,
        offset,
        limit,
    )


@documents_router.get(
    "/documents/{document_id}",
    response_model=Document,
)
def get_document(
    document_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.user != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own documents",
        )

    return document


@documents_router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.user != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own documents",
        )

    delete_document_db(db, document_id)

    return {"message": "Document deleted"}


@documents_router.patch(
    "/documents/{document_id}",
    response_model=Document,
)
def update_document(
    document_id: int,
    updated_document: DocumentUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.user != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own documents",
        )

    return update_document_db(
        db,
        document_id,
        updated_document.title,
    )