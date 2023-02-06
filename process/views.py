from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .serializers import SubscribeSerializer
from payments.settings import PAYME_SETTINGS
import requests
from rest_framework.parsers import JSONParser 
from rest_framework import status

import os
from supabase.client import Client, create_client
from dotenv import load_dotenv
from random import randint
load_dotenv()
from .models import *

orders_fields = ('order_amount', 'fulfillment_status', 'owner')
transaction_fileds = ('status', 'transaction_token', 'customer_id', 'order_id')
customers_fields = ('full_name', 'email', 'phone', 'address')

# TEST ENDPOINT URL https://checkout.test.paycom.uz/api
# AUTHORIZATION X-Auth: {id}:{password}  
# Test page link https://developer.help.paycom.uz/protokol-subscribe-api


AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_ID'], 
                                          PAYME_SETTINGS['PAY_ME_TEST_KEY'])}


URL = 'https://checkout.test.paycom.uz/api'

supabase = SupabaseActions()

class CardsCreate(APIView):
    
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False)
        if serializer.is_valid(raise_exception=True):
            response = serializer.validated_data
        
            return response
        else:
            raise KeyError
        
    


class CardsCheck(APIView):
    '''Проводятся операции проверки удаления банковской карты клиента.
       Используется токен передаваемый от клиентской части.'''
    
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["info"]["token"]  # after decoding 
        # from json we get validated data. Validated data returns a python dictionary.
        result = self.cards_check(token)
        
        # data = supabase.process_input_data(serializer.validated_data["info"], customers_fields)
        # supabase.db_login()
        # supabase.db_save(validated_data=data, table_name='customer')
        
        return Response(result)


    def cards_check(self, token):

        data = {
                    "id": 123,
                    "method": "cards.check",
                    "params": {
                        "token": token
                    }
        }
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        # if 'error' in response.json():
        #     return response.json()
        
        
        return response



class CardsRemove(APIView):
    '''Проводятся операции удаления банковской карты клиента. 
    Используется токен передаваемый от клиентской части.'''
    
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
        serializer.is_valid()
        token = serializer.validated_data["info"]["token"]  # after decoding from json we get validated data. Validated data returns a python dictionary.
        result = self.cards_remove(token)    
        return Response(result)

    def cards_remove(self, token, ):

        data = {
                    "id": 123,
                    "method": "cards.remove",
                    "params": {
                        "token": token
                    }
        }
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response



class Receipts(APIView):
    
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
        serializer.is_valid()
        result = self.receipts_create(serializer.validated_data)
        return Response(result)
        # token = serializer.validated_data["info"]["token"]  # after decoding 
        # from json we get validated data. Validated data returns a python dictionary.
        
        
    def receipts_create(self, validated_data):
        
        data = {    
                "id": 123,
                "method": "receipts.create",
                "params":{
                            "amount": validated_data["params"]["amount"],
                            "account":  {
                                            "user_id" : validated_data["params"]["account"]["user_id"],
                                            "email" : validated_data["params"]["account"]["email"],
                                            "phone" : validated_data["params"]["account"]["phone"],
                                        },

                            }}
        
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        if 'error' in result:
            return result
        
        # database operations needed
        
        result = self.receipts_pay(validated_data)
        return result

    def receipts_pay(self, validated_data):

        data = {
                    "id": 123,
                    "method": "receipts.pay",
                    "params": {
                                "id": validated_data["params"]["id"],  #ID чека
                                "token": validated_data["params"]["token"],
                                }
                }
        
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response


    def receipts_send(self, request):
        ...













    # def receipts_check(self, request):
    #     ...


    # def receipts_get(self, request):
    #     ...
        
        





    # def receipts_cancel(self, request):
    #     ...
        
        
    # def receipts_get_all(self, request):
    #     ...











# class CardsCheck(APIView):
#     '''Проверяем токен пластиковокй карты от фронта'''
    
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
#         serializer.is_valid()
#         token = serializer.validated_data['params']['token']  # after decoding from json we get validated data. Validated data returns a python dictionary.
#         return Response(token)
    
    
#     def card_check(self, token)
#     # def post(self, request):
#     #     message = request.data.get("token")
#     #     return Response({'token': message})

# class CardsRemove(APIView):
#     '''Удаляем токен пластиковокй карты от фронта'''
    
#     def delete(self, request):
#         message = request.data.get("token")
#         return Response({'token': message})
    
    
# class ReceiptsCreate(APIView):
#     '''Создание чека на оплату'''
    
#     def delete(self, request):
#         message = request.data.get("token")
#         return Response({'token': message})
    




def index(request):
    return HttpResponse('Index')


def main(request):
    return HttpResponse('main')


# class PaymentApiView(APIView):

#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
#         serializer.is_valid()
#         token = serializer.validated_data['params']['token']  # after decoding from json we get validated data. Validated data returns a python dictionary.
#         result = self.receipts_create(token, serializer.validated_data)
#         return Response(result)
    

#     def receipts_create(self, token, validated_data):
#         key_2 = validated_data['params']['account'][KEY_2] if KEY_2 else None
#         data = dict(
#             id=validated_data['id'],
#             method='receipts.create',
#             params=dict(
#                 amount=validated_data['params']['amount'],
#                 account=validated_data['params']['account'],
#         ))
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response.json()
#         if 'error' in result:
#             return result


#     def receipts_pay(self, trans_id, token):
#         data = dict(
#             method='receipts.pay',
#             params=dict(
#                 id=trans_id,
#                 token=token,
#             )
#         )
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response.json()
#         return result