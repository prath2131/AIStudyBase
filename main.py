from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from database import engine, create_db_and_tables, Document, Page
from pypdf import PdfReader
from sqlmodel import Field, Session


app = FastAPI()


# creating a database session dependency in FastAPI using engine.
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_text_by_page(filename):
    reader = PdfReader(filename)
    extracted_page = []
    for i in range(len(reader.pages)):
        extracted_page.append(reader.pages[i].extract_text())
    return extracted_page


@app.post(
    "/uploadfile/",
    summary="Upload document file",
    description="accepts a file upload "
)
def create_upload_file(session: SessionDep, file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}

    extracted_page = get_text_by_page(file.file)
    document = Document(
        filename=file.filename,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    for i in range(len(extracted_page)):
        page_row= Page(
            document_id=document.id,
            page_number=i+1,
            text= extracted_page[i]
        )
        session.add(page_row)
    session.commit()
    return {
        "id": document.id,
        "preview": extracted_page[0][:200] if extracted_page else ""
    }








