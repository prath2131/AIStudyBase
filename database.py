from uuid import UUID
from typing import List, Optional
from sqlmodel import Session, SQLModel, create_engine, Field, Relationship
import os
from dotenv import load_dotenv
from datetime import datetime,timezone

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


class Document(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    pages: List["Page"] = Relationship(back_populates="document")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: UUID


class Page(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    page_number: int
    text: str
    document: Optional[Document] = Relationship(back_populates="pages")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)




