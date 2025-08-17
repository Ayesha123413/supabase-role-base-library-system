
from decouple import config;
from supabase import create_client, Client

url=config("SUPABASE_URL")
key=config("SUPABASE_KEY")
service_role_key=config("SUPABASE_SERVICE_ROLE_KEY")


supabase : Client =create_client(url,key)

supabase_admin: Client = create_client(url, service_role_key)