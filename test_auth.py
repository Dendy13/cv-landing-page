import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("backend/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
try:
    print("Testing auth...")
    # Intentionally use a bad password to see what exception it throws
    res = supabase.auth.sign_in_with_password({"email": "test@example.com", "password": "wrong"})
    print("Success:", res)
except Exception as e:
    print("Exception type:", type(e))
    print("Exception msg:", str(e))
