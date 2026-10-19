from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict


class Document(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    user: str
    data: date
    created_at: datetime


class DocumentCreate(BaseModel):
    title: str = Field(min_length=2)
    filename: str = Field(min_length=2)


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=2)
