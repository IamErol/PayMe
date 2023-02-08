from django.db import models
import os
from supabase.client import Client, create_client
from dotenv import load_dotenv
from random import randint
load_dotenv()


# orders_fields = ('order_amount', 'fulfillment_status', 'owner')
# transaction_fileds = ('status', 'transaction_token', 'customer_id', 'order_id')
# user = ...
orders_fields = ('order_amount', 'fulfillment_status', 'owner')
transaction_fileds = ('status', 'transaction_token', 'customer_id', 'order_id')
customers_fields = ('full_name', 'email', 'phone', 'address')
class SupabaseActions:

    def __init__(self, url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL", default=''),
                 key: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", default=''),
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
    
        
    def process_input_data(self, validated_data: dict, fields: tuple) -> dict:
        '''Takes dictionary from post request and extracts fields that exists in 
           certain database table'''
        key = [a for a in validated_data if a in fields]
        value = [validated_data[a] for a in validated_data if a in fields]
        
        data = dict(zip(key, value))
        return data
     
    
    @staticmethod
    def dict_check(data: dict):
        if data:
            print(f'static: {data}')
        else:
            raise ValueError


    def db_save(self, validated_data: dict, table_name: str):   
        '''Saves data to specified table in database''' 
        SupabaseActions.dict_check(validated_data)    
        supabase: Client = create_client(self.url, self.key)
        try:
            supabase.table("transaction").insert(validated_data).execute()
        except:
            raise KeyError
        
        return None

