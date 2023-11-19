"""Here performed logic for working with Supabase as main database."""
from django.db import models
import os
from supabase.client import create_client, Client
from dotenv import load_dotenv

load_dotenv()

ORDER_FIELDS = ('order_amount', 'fulfillment_status', 'owner')
TRANSACTION_FIELDS = ('status', 'transaction_token', 'customer_id', 'order_id')
CUSTOMER_FIELDS = ('full_name', 'email', 'phone', 'address')


class SupabaseActions:
    """Class for working with Supabase."""

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

    def process_input_data(self, validated_data: dict, fields: tuple) -> dict:
        """
        Takes dictionary from post request and extracts fields that exists in
        certain database table.
        """
        key = [a for a in validated_data if a in fields]
        value = [validated_data[a] for a in validated_data if a in fields]

        data = dict(zip(key, value))
        return data

    @staticmethod
    def dict_check(data: dict):
        if data:
            return data
        else:
            raise ValueError

    def db_save(self, validated_data: dict):
        """Saves data to specified table in database."""
        SupabaseActions.dict_check(validated_data)
        supabase: Client = create_client(self.url, self.key)
        try:
            supabase.table("transaction").insert(validated_data).execute()
        except KeyError as e:
            raise KeyError(f"Key {e} not found in table.")

    def supabase_login(self):
        """Login to Supabase."""
        supabase: Client = create_client(self.url, self.key)
        return supabase

    def transactions_data_to_insert(self, result, validated_data) -> dict:
        """Get transactoin data to insert to database."""
        transaction_data = {"status": result["result"]['receipt']['state'],
                            "order_id": result["result"]['transaction_order_id'],
                            "user_id": validated_data["params"]['account']["user_id"],
                            "cards_token": validated_data["params"]["token"],
                            "amount": str(result["result"]['receipt']['amount'])[:-2],
                            "receipts_id": result["result"]['receipt']['_id'],
                            "request_id": validated_data["params"]['post_id'],
                            "cash": validated_data["params"]['cash']}
        return transaction_data

    def orders_data_to_insert(self, result, validated_data) -> dict:
        """Get order data to insert to database."""
        order_data = {
            "user_id": validated_data["params"]['account']["user_id"],
            "order_amount": str(result["result"]['receipt']['amount'])[:-2],
            "status": validated_data["params"]['status'],
            "positions": validated_data["params"]['positions'],
            "transaction_id": result["result"]['transaction_order_id'],
            "user_data": validated_data["params"]['account']
        }
        return order_data

    def insert_data(self, data_to_insert: dict, table_name: str):
        """Insert data to specified table in database."""
        supabase: Client = create_client(self.url, self.key)
        supabase.table(table_name).insert(data_to_insert).execute()

    def delete_basket(self, user_id):
        """Delete basket from database."""
        supabase: Client = create_client(self.url, self.key)
        try:
            raw_basket = supabase.table("users-data").select("basket").eq("id", user_id).execute()
            basket = raw_basket.data[0]['basket']
            for item in basket:
                supabase.table("basket").delete().eq("id", item).execute()
        except KeyError:
            return supabase.table("users-data").select("basket").eq("id", user_id).execute()

    def delete_user_basket(self, user_id):
        """Delete user basket from database."""
        supabase: Client = create_client(self.url, self.key)
        try:
            supabase.table("users-data").update({"basket": []}).eq("id", user_id).execute()
        except KeyError:
            return supabase.table("users-data").update({"basket": []}).eq("id", user_id).execute()
