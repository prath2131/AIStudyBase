from typing import Annotated
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from database import engine, create_db_and_tables, Document, Page
from pypdf import PdfReader
from sqlmodel import Session, select
from pydantic import BaseModel
from fastapi.security import HTTPBearer
from uuid import UUID

# supabase setup
from supabase import Client, create_client
from supabase_auth.errors import AuthApiError
from dotenv import load_dotenv
import os

app = FastAPI()
security = HTTPBearer()

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 8000))
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL or SUPABASE_KEY. Did you create a .env file? "
        "See .env.example for the expected format."
    )
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


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


def get_current_user(credentials=Depends(security)):

    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )
    try:
        response = supabase.auth.get_user(token)
        return response.user.id
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


@app.post(
    "/documents/",
    summary="Upload document file",
    description="accepts a file upload "
)
def create_upload_file(
    session: SessionDep,
    current_userid: str = Depends(get_current_user),
    file: UploadFile | None = None
):
    if not file:
        return {"message": "No upload file sent"}

    extracted_page = get_text_by_page(file.file)
    document = Document(
        filename=file.filename,
        owner_id=UUID(current_userid)
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    for i in range(len(extracted_page)):
        page_row = Page(
            document_id=document.id,
            page_number=i+1,
            text=extracted_page[i]
        )
        session.add(page_row)
    session.commit()
    return {
        "id": document.id,
        "preview": extracted_page[0][:200] if extracted_page else ""
    }


class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None


@app.post(
    "/auth/signup",
    status_code=201,
    summary="Register a new user",
    description="Creates new user using provided credentials"
)
def signup(user: AuthRequest):
    if not user.email or not user.password:
        return JSONResponse(
            status_code=400,
            content={"error": "email and password are required"}
        )

    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
        return response.user.model_dump()
    except AuthApiError as e:
        return JSONResponse(
            status_code=400,
            content={"error":  str(e)}
        )


@app.post(
    "/auth/login",
    summary="Authenticate a user",
    description="Verifies the credentials"
)
def login(user: AuthRequest):
    if not user.email or not user.password:
        return JSONResponse(
            status_code=400,
            content={"error": "email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password,
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except AuthApiError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )


@app.get(
    "/documents/",
    summary="Get documents protected"
)
def get_document(
    session: SessionDep,
    current_userid: str = Depends(get_current_user),
):

    statement = select(Document).where(Document.owner_id == UUID(current_userid))
    document = session.exec(statement).all()
    return document


@app.get("/debug/db")
def debug_db():
    return {"db_url": str(engine.url)}