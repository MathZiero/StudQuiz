import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("supabase_sec") or os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {url}")
print(f"Key type used: {'Secret (service_role)' if os.getenv('supabase_sec') else 'Public (anon)'}")

if url:
    url = url.strip()
    if url.endswith("/rest/v1/"):
        url = url.replace("/rest/v1/", "")
    elif url.endswith("/rest/v1"):
        url = url.replace("/rest/v1", "")

try:
    client = create_client(url, key)
    print("Client created successfully!")
    response = client.table("questoes").select("*").limit(1).execute()
    print("Test connection and query successful!")
    print(f"Returned data: {response.data}")
except Exception as e:
    print(f"Error connecting or querying: {e}")
