from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SubscribeSerializer
import requests
from payments.settings import PAYME_SETTINGS
import os
from supabase.client import Client, create_client
from dotenv import load_dotenv
from random import randint
load_dotenv()
from .models import *
from .pay_me_methds import *
from . import post_calls
import secrets
from django.http import HttpResponse
import logging

# logger = logging.getLogger(__name__)

orders_fields = ('order_amount', 'fulfillment_status', 'owner')
transaction_fileds = ('status', 'transaction_token', 'customer_id', 'order_id')
customers_fields = ('full_name', 'email', 'phone', 'address')

# TEST ENDPOINT URL https://checkout.test.paycom.uz/api
# AUTHORIZATION X-Auth: {id}:{password}  
# Test page link https://developer.help.paycom.uz/protokol-subscribe-api


AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_ID'], 
                                          PAYME_SETTINGS['PAY_ME_TEST_KEY'])}

# AUTHORIZATION = {'X-Auth': '63e3720d1afcb4de778fe872'}# test virtual terminal

FRONT_AUTH = {'X-Auth':'63e3720d1afcb4de778fe872'}



# URL = 'https://checkout.paycom.uz/api'
URL = 'https://checkout.test.paycom.uz/api'


# supabase = SupabaseActions()

class CardsCreate(APIView):
    
    def post(self, request):
        post_id = secrets.randbits(32) # generating id number for post requests to PayMe.
        
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        validated_data.update(post_id=str(post_id)) # including id number for future post requests to PayMe.
        
        result = self.card_create(validated_data=validated_data) # calling card creation.
        if 'error' in result:
            return Response({
                             "income_data":validated_data,
                             "result":result,
                             "fail": "start"})
        
        return Response(result)
    
    
    def card_create(self, validated_data):
        '''
        Создание токена пластиковой карты.
        '''
  
        result = post_calls.post_card_create(validated_data, URL, FRONT_AUTH)
        token = result['result']['card']['token']

        if 'error' in result:
            result.update(fail='at card_create', token=token)
            return result

        return result
        result = self.card_get_verify_code(token, validated_data) # calls sms verification function.
        
        # supabase.db_login()
        # data = supabase.table("customer").insert({"full_name":"Joe",
        #                                           "email":'hello@mail.com',
        #                                           "phone": 123123,
        #                                           "address": "add"}).execute()
        # result.update(post_id=(validated_data['post_id']))
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
        '''Отправка токена для валидации карты.'''

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
        '''Проверка токена карты.'''

        data = dict(
            id=int(validated_data['params']['post_id']),
            method=CARD_CHECK,
            params=dict(
                        token=validated_data['params']['token']
            )
        )
        
        response = requests.post(URL, json=data, headers=FRONT_AUTH)
        result = response.json()
        
        token=validated_data['params']['token']
        if 'error' in result:
            remove = self.card_remove(token, validated_data)
            result.update(fail='cards check', remove_response=remove)
            return result

        result = self.receipts_create(validated_data)
        return result
        


    def receipts_create(self, validated_data):
        '''Создание чека на оплату.'''
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=RECEIPTS_CREATE,
            params=dict(
                amount=float(validated_data['params']['amount']),
                account=dict(
                    phone = str(validated_data['params']['account']['phone']),
                    email = str(validated_data['params']['account']['email']),
                    user_id = validated_data['params']['account']['user_id'],
                items=dict(
                    code = '03926001005000000',
                    vat_percent = 0,
                    units= 796,
                    package_code = '1522896',
                    
                )
                
                )
            )
        )
        
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response.json()  
         
        
        token=validated_data['params']['token']
        if 'error' in result:
            receipt = result
            
            result = self.card_remove(token, validated_data)
            result.update(fail='receipt create', receipt=receipt)
            return result
        
        receipt_id = result['result']['receipt']['_id']
        token=validated_data['params']['token']
        
        
        result = self.receipts_pay(receipt_id, token, validated_data)
        result.update(status='receipt paid')
        return result   
    
    
    
    def receipts_pay(self, receipt_id, token, validated_data):
        '''
        Производится оплата чека.
        '''
        
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=RECEIPTS_PAY,
            params=dict(
                id=str(receipt_id),
                token=str(token),
            )
        )
        
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response.json()


        if 'error' in result:
            receipts_pay_response = result
            result = self.card_remove(token, validated_data)
            result.update(fail='pay', data=data, token=token, receipts_pay_response=result)
            return result
        
        if result['result']['receipt']['state'] == '4':
            # db actions here
            pass

        result.update(status='pay success')
        return result


    def card_remove(self, token, validated_data):
        '''
        Удаление токена карты.
        '''
        
        data = dict(
            id=int(validated_data['params']['post_id']),
            method=CARD_REMOVE,
            params=dict(
                token=token,
            )
        )
        response = requests.post(URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        
        
        if 'error' in result:
            result.update(token=token, fail='remove')
            return result
        
        result.update(cardremoved='cardremoved')
        return result
    
    
    

 







    # def cards_check(self, token, post_id):
    #     '''Проверка токена карты.'''

    #     data = dict(
    #         id=123123123,
    #         method=CARD_CHECK,
    #         params=dict(
    #                     token=token
    #         )
    #     )
        
    #     response = requests.post(URL, json=data, headers={'X-Auth':'63db5082f0a18aaf5ec5bb3b'})
    #     result = response.json()
    #     if 'error' in result:
    #         return result

        
    #     return response
    
    
# class CardVerify(APIView):

#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False)
#         serializer.is_valid(raise_exception=True)
#         result = self.card_verify(serializer.validated_data)
        

#         return Response(result)

#     def card_verify(self, validated_data):
#         data = dict(
#             id=111222333444,
#             method=CARD_VERIFY,
#             params=dict(
#                 token=validated_data['params']['token'],
#                 code=validated_data['params']['code'],
#             )
#         )
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response.json()

#         return result







 
# class Receipts(APIView): 
    
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False)
#         serializer.is_valid(raise_exception=True)
#         token = serializer.validated_data['params']['token']
#         result = self.receipts_create(token=token, validated_data=serializer.validated_data)

#         return Response(result)
    
    
   
    # def receipts_create(self, token, validated_data):

    #     data = dict(
    #         id=111222333444,
    #         method=RECEIPTS_CREATE,
    #         params=dict(
    #             amount=validated_data['params']['amount'],
    #             account=dict(
    #                 phone = validated_data['params']['phone'],
    #                 email = validated_data['params']['email'],
    #                 user_id = validated_data['params']['user_id'],
    #             )
    #         )
    #     )
        
    #     response = requests.post(URL, json=data, headers=AUTHORIZATION)
    #     result = response.json()    
    #     if 'error' in result:
    #         return result
        
    #     receipt_id = result['result']['receipt']['_id']
        
    #     result = self.receipts_pay(receipt_id, token)
    #     return result   
    
    
    
    # def receipts_pay(self, receipt_id, token):
    #     data = dict(
    #         id=111222333444,
    #         method=RECEIPTS_PAY,
    #         params=dict(
    #             id=receipt_id,
    #             token=token,
    #         )
    #     )
    #     response = requests.post(URL, json=data, headers=AUTHORIZATION)
    #     result = response.json()


    #     if 'error' in result:
    #         return result

    #     return result
    
       
        
        
        
        
        
           
    # def card_get_verify_code(self, token):
    #     data = dict(
    #         method=CARD_GET_VERIFY_CODE,
    #         params=dict(
    #             token=token
    #         )
    #     )
    #     response = requests.post(URL, json=data, headers=AUTHORIZATION)
    #     result = response.json()
    #     if 'error' in result:
    #         return result

    #     result.update(token=token)
    #     return result


# class CardsVerify(APIView):

#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False)
#         serializer.is_valid(raise_exception=True)
#         result = self.card_verify(serializer.validated_data)

#         return Response(result)

#     def card_verify(self, validated_data):
#         data = dict(
#             # id=validated_data['id'],
#             id=secrets.randbits(32),
#             method=CARD_VERIFY,
#             params=dict(
#                 token=validated_data['params']['token'],
#                 code=validated_data['params']['code'],
#             )
#         )
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response.json()

#         return result
    
        
    


# class CardsCheck(APIView):
#     '''Проводятся операции проверки удаления банковской карты клиента.
#        Используется токен передаваемый от клиентской части.'''
    
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
#         serializer.is_valid(raise_exception=True)
#         token = serializer.validated_data["info"]["token"]  # after decoding 
#         # from json we get validated data. Validated data returns a python dictionary.
#         result = self.cards_check(token)
        
#         # data = supabase.process_input_data(serializer.validated_data["info"], customers_fields)
#         # supabase.db_login()
#         # supabase.db_save(validated_data=data, table_name='customer')
        
#         return Response(result)


#     def cards_check(self, token):


#         data = dict(
#             # id=validated_data['id'],
#             id=secrets.randbits(32),
#             method=CARD_CHECK,
#             params=dict(
#                         token=token
#             )
#         )

#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         if 'error' in response.json():
#             return response.json()
        
        
#         return response



# class CardsRemove(APIView):
#     '''Проводятся операции удаления банковской карты клиента. 
#     Используется токен передаваемый от клиентской части.'''
    
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
#         serializer.is_valid()
#         token = serializer.validated_data["info"]["token"]  # after decoding from json we get validated data. Validated data returns a python dictionary.
#         result = self.cards_remove(token)    
#         return Response(result)

#     def cards_remove(self, token, ):

#         data = {
#                     "id": 123,
#                     "method": "cards.remove",
#                     "params": {
#                         "token": token
#                     }
#         }
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response



# class Receipts(APIView):
    
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
#         serializer.is_valid()
#         result = self.receipts_create(serializer.validated_data)
#         return Response(result)
#         # token = serializer.validated_data["info"]["token"]  # after decoding 
#         # from json we get validated data. Validated data returns a python dictionary.
        
        
#     def receipts_create(self, validated_data):
        
#         data = {    
#                 "id": 123,
#                 "method": "receipts.create",
#                 "params":{
#                             "amount": validated_data["params"]["amount"],
#                             "account":  {
#                                             "user_id" : validated_data["params"]["account"]["user_id"],
#                                             "email" : validated_data["params"]["account"]["email"],
#                                             "phone" : validated_data["params"]["account"]["phone"],
#                                         },

#                             }}
        
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response.json()
#         if 'error' in result:
#             return result
        
#         # database operations needed
        
#         result = self.receipts_pay(validated_data)
#         return result

#     def receipts_pay(self, validated_data):

#         data = {
#                     "id": 123,
#                     "method": "receipts.pay",
#                     "params": {
#                                 "id": validated_data["params"]["id"],  #ID чека
#                                 "token": validated_data["params"]["token"],
#                                 }
#                 }
        
#         response = requests.post(URL, json=data, headers=AUTHORIZATION)
#         result = response


#     def receipts_send(self, request):
#         ...













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
    
    
    # def card_check(self, token)
    # def post(self, request):
    #     message = request.data.get("token")
    #     return Response({'If you see it then, it is working': message})

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




# def post(self, request):
#     data = request.data
#     return Response({'If you see it then, it is working': data})