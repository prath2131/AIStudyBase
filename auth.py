# supabase setup
from supabase import Client, create_client
from dotenv import load_dotenv
import os


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