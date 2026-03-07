import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY is missing. Ensure you have a .env file set up.")

def get_supabase_client() -> Client:
    # We initialize the client inside a function or lazily, in case the environment isn't fully set immediately
    return create_client(SUPABASE_URL or "", SUPABASE_KEY or "")

# Creating a singleton instance to use across the backend
supabase: Client = get_supabase_client()
