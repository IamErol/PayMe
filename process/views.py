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

# TEST ENDPOINT URL https://checkout.test.paycom.uz/api
# AUTHORIZATION X-Auth: {id}:{password}  
# Test page link https://developer.help.paycom.uz/protokol-subscribe-api


AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_ID'], PAYME_SETTINGS['PAY_ME_TEST_KEY'])}
URL = 'https://checkout.test.paycom.uz/api'





class CardsCheck(APIView):
    '''Проверяем токен пластиковокй карты от фронта'''
    
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False) #data = dict object from request
        serializer.is_valid()
        token = serializer.validated_data["params"]["token"]  # after decoding from json we get validated data. Validated data returns a python dictionary.
        result = self.cards_check(token)
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
        result = response.json()

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