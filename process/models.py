from django.db import models
import os
from supabase.client import create_client, Client
from dotenv import load_dotenv
from random import randint
load_dotenv()


class SupabaseActions:
    def __init__(self, url: str = os.getenv("SUPABASE_URL", default=''),
                 key: str = os.getenv("SUPABASE_KEY", default=''),
                 email: str = os.getenv("SUPABASE_USER_EMAIL", default=''),
                 password: str = os.getenv("SUPABASE_USER_PASSWORD", default=''),) -> None:
        self.url = url
        self.key = key
        self.email = email
        self.password = password
    
    def db_login(self):
        supabase: Client = create_client(self.url, self.key)
        supabase.auth.sign_out()
        session = supabase.auth.sign_in(email=self.email, password=self.password)
        return supabase


    def db_save(self, validated_data: dict):
                
        supabase: Client = create_client(self.url, self.key)
        try:
            supabase.table("transaction").insert(validated_data).execute()
        except:
            raise KeyError
        
        return None