from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SubscribeSerializer
import requests
from payments.settings import PAYME_SETTINGS
import os
from supabase.client import Client, create_client
from dotenv import load_dotenv
from random import randint
from .models import *
from .pay_me_methds import *
from . import post_calls
import secrets
from django.http import HttpResponse
import logging
import uuid
import datetime
load_dotenv()

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# TEST_FRONT_AUTH = {'X-Auth':'63e4bca666d78f1f2b02c088'}


stage = os.getenv('STAGE')
sup = SupabaseActions()
sup.supabase_login()


if stage == 'test':
    URL = PAYME_SETTINGS['TEST_URL']
    FRONT_AUTH = {'X-Auth': '{}'.format(PAYME_SETTINGS['PAY_ME_TEST_ID'])}
    AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_TEST_ID'],
                                          PAYME_SETTINGS['PAY_ME_TEST_KEY'])}
else:
    if stage == 'prod':
        URL = PAYME_SETTINGS['PROD_URL']
        FRONT_AUTH = {'X-Auth': '{}'.format(PAYME_SETTINGS['PAY_ME_PROD_ID'])}
        AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_PROD_ID'], 
                                            PAYME_SETTINGS['PAY_ME_PROD_KEY'])}
    


class CardsCreate(APIView):
    '''
    Creates token and verifies debit card with sms verification.
    '''
    
    def post(self, request):
        post_id = int(secrets.randbits(32)) # generating id number for post requests to PayMe.
        order_id = str(uuid.uuid4())

        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        validated_data.update(post_id=post_id, order_id= order_id) # including id number for future post requests to PayMe.
        
        result = self.card_create(validated_data=validated_data) # calling card creation.
        if 'error' in result:
            return Response({
                             "income_data":validated_data,
                             "result":result,
                             "fail": "start"})
            
        
        # ORDERS = sup.orders_data_to_insert(result, validated_data)  
        # sup.insert_data(ORDERS, 'orders')
        return Response(result)
    
    
    def card_create(self, validated_data):
        '''
        Создание токена пластиковой карты.
        '''
        result = post_calls.post_card_create(validated_data, URL, FRONT_AUTH)

        if 'error' in result:
            result.update(fail='at card_create')
            return result

        token = result['result']['card']['token']
        result = self.card_get_verify_code(token, validated_data) # calls sms verification function.
        return result  # returns messge sent status.
    
    
    def card_get_verify_code(self, token, validated_data):
        '''
        Получение смс кода для верификации карты.
        '''
        result = post_calls.post_card_get_verify_code(validated_data, token, URL, FRONT_AUTH)
        
        if 'error' in result:
            result.update(fail='card_get_verify_code')
            return result

        result.update(token=token)
        return result    

    
class CardVerify(APIView):
    """Verify card"""

    def post(self, request):
        '''
        Takes post request from client and sends post request to PayMe.
        '''
           
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        result = self.card_verify(validated_data)
        
        return Response(result)  # returns result in Json format using Response(dict)
    

    def card_verify(self, validated_data):
        """Sends code to Payme to verify card."""
        result = post_calls.post_card_verify(validated_data, URL, FRONT_AUTH)
        
        if 'error' in result:
            token = validated_data['params']['token'] 
            data = result
            result = self.card_remove(token, validated_data)
            result.update(fail='card_verify, card removed', data=data)
            return result

        # result = self.receipts_create(validated_data)
        result = self.cards_check(validated_data)
        return result
    
    
    def cards_check(self, validated_data):
        """Checking if token is valid"""
        result = post_calls.post_card_check(validated_data, URL, FRONT_AUTH)
                
        token=validated_data['params']['token']
        if 'error' in result:
            remove = self.card_remove(token, validated_data)
            result.update(fail='cards check', remove_response=remove)
            return result

        result = self.receipts_create(validated_data)
        return result
        

    def receipts_create(self, validated_data):
        """Cretes receipts for further payment"""
        result = post_calls.post_receipts_create(validated_data, URL, AUTHORIZATION)
         
        token=validated_data['params']['token']
        if 'error' in result:
            receipt = result
            
            result = self.card_remove(token, validated_data)
            result.update(fail='receipt create', receipt=receipt)
            return result
        
        receipt_id = result['result']['receipt']['_id']
        
        result = self.receipts_pay(receipt_id, token, validated_data)
        return result   
        
    
    def receipts_pay(self, receipt_id, token, validated_data):
        """Initialization of a payment"""
        transaction_order_id = str(uuid.uuid4())
        result = post_calls.post_receipts_pay(validated_data, URL, AUTHORIZATION, receipt_id, token)
        

        if 'error' in result:
            receipts_pay_response = result
            result = self.card_remove(token, validated_data)
            result.update(fail='pay', token=token, receipts_pay_response=result)
            return result
        

        TRANSACTION = sup.transactions_data_to_insert(result, validated_data)
        ORDERS = sup.orders_data_to_insert(result, validated_data)
        sup.insert_data(TRANSACTION, 'transactions')
        sup.insert_data(ORDERS, 'orders')
        result.update(data_is_saved='True')

            

        result.update(status='pay success')
        return result


    def card_remove(self, token, validated_data):
        """Deleting card token."""
        result = post_calls.post_card_remove(validated_data, URL, AUTHORIZATION, token)
        
        if 'error' in result:
            result.update(token=token, fail='remove')
            return result
        
        result.update(cardremoved='cardremoved')
        return result


def index(request):
    return HttpResponse('Index')


def main(request):
    return HttpResponse('main')