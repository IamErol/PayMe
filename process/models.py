from django.db import models
import os
from supabase.client import create_client, Client
from dotenv import load_dotenv
from random import randint
load_dotenv()


class SupabaseActions:
    
    
    def db_login(self):
        url: str = os.getenv("SUPABASE_URL", default='')
        key: str = os.getenv("SUPABASE_KEY", default='')
        email: str = os.getenv("SUPABASE_USER_EMAIL", default='')
        password: str = os.getenv("SUPABASE_USER_PASSWORD", default='')
        
        supabase: Client = create_client(url, key)
        supabase.auth.sign_out()
        session = supabase.auth.sign_in(email=email, password=password)
        return supabase


    def db_save(self, validated_data: dict,
                url: str = os.getenv("SUPABASE_URL", default=''),
                key: str = os.getenv("SUPABASE_KEY", default='')):
                
        supabase: Client = create_client(url, key)
        try:
            supabase.table("transaction").insert(validated_data).execute()
        except:
            raise KeyError
        
        return None