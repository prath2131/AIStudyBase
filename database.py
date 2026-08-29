
from sqlmodel import Field, Session, SQLModel, create_engine, select
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


class Document(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    extracted_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)




