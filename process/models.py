import os
from supabase.client import create_client, Client
from dotenv import load_dotenv
load_dotenv()




class SupabaseActions:
    customers = ('full_name', 'email', 'phone', 'address')
    
    def __init__(self,
                 url: str = os.getenv("SUPABASE_URL", default=''),
                 key: str = os.getenv("SUPABASE_KEY", default=''),
                 email: str = os.getenv("SUPABASE_USER_EMAIL", default=''),
                 password: str = os.getenv("SUPABASE_USER_PASSWORD", default=''),
                 ) -> None:
        
        self.url = url
        self.key = key
        self.email = email
        self.password = password
    
    def supabase_login(self):
        supabase: Client|None = create_client(self.url, self.key)
        return supabase
    
    def transactions_data_to_insert(self, result, validated_data) -> dict:
        

        transaction_data = {"status":result["result"]['receipt']['state'], 
                "order_id":result["result"]['transaction_order_id'], 
                "user_id":validated_data["params"]['account']["user_id"], 
                "cards_token":validated_data["params"]["token"], 
                "amount":str(result["result"]['receipt']['amount'])[:-2], 
                "receipts_id":result["result"]['receipt']['_id'], 
                "request_id":validated_data["params"]['post_id'],
                "cash":validated_data["params"]['cash']}
        return transaction_data

        
        
    
    def orders_data_to_insert(self, result, validated_data) -> dict:
        
        
        order_data = {
                            "user_id":validated_data["params"]['account']["user_id"],
                            "order_amount":str(result["result"]['receipt']['amount'])[:-2],
                            "status":result["result"]['receipt']['state'], 
                            "positions":validated_data["params"]['positions'], 
                            "transaction_id":result["result"]['transaction_order_id'],
                            "user_data":validated_data["params"]['account']
                            }
        return order_data

        
        
    
            
        

    def insert_data(self, data_to_insert: dict, table_name: str):  
        supabase: Client = create_client(self.url, self.key)
        supabase.table(table_name).insert(data_to_insert).execute()
        return None


    def delete_basket(self, user_id, table_name, supa_client):
        supabase: Client = supa_client
        basket = supabase.table(table_name).select("positions").eq("user_id", user_id).execute()
        for item in basket:
            supabase.table("countries").delete().eq("id", item).execute()
            
    def delete_user_basket(self, user_id, table_name, supa_client):
        supabase: Client = supa_client
        supabase.table(table_name).update({"basket": []}).eq("id", user_id).execute()














































# from django.db import models
# import os
# from supabase.client import Client, create_client
# from dotenv import load_dotenv
# from random import randint
# from supabase.client import create_client, Client
# load_dotenv()


# orders_fields = ('order_amount', 'status', 'user', 'positions')
# transactions_fileds = ('status', 'order_id', 'user_id', 'cards_token', 'amount', 'receipts_id')
# customers_fields = ('full_name', 'email', 'phone', 'address')
# class SupabaseActions:

#     def __init__(self, 
#                  url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL", default=''),
#                  key: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", default=''),
#                  email: str = os.getenv("SUPABASE_USER_EMAIL", default=''),
#                  password: str = os.getenv("SUPABASE_USER_PASSWORD", default=''),) -> None:
        
#         self.url = url
#         self.key = key
#         self.email = email
#         self.password = password
        
#     def db_login(self):
#         supabase: Client = create_client(self.url, self.key)
#         supabase.auth.sign_out()
#         # session = supabase.auth.sign_in(email=self.email, password=self.password)
#         return supabase
    
        
#     def process_input_data(self, payme_response: dict, fields: tuple) -> dict:
#         '''Takes dictionary from post request and extracts fields that exists in 
#            certain database table'''
#         key = [a for a in payme_response if a in fields]
#         value = [payme_response[a] for a in payme_response if a in fields]
        
#         data = dict(zip(key, value))
#         return data
     
    
#     @staticmethod
#     def dict_check(data: dict):
#         if data:
#             print(f'static: {data}')
#         else:
#             raise ValueError


#     def db_save(self, validated_data: dict, table_name: str):   
#         '''Saves data to specified table in database''' 
#         SupabaseActions.dict_check(validated_data)    
#         supabase: Client = create_client(self.url, self.key)
#         try:
#             supabase.table(table_name).insert(validated_data).execute()
#         except:
#             raise KeyError
        
#         return None

        # data = supabase.process_input_data(serializer.validated_data["info"], customers_fields)
        # supabase.db_login()
        # supabase.db_save(validated_data=data, table_name='customer')