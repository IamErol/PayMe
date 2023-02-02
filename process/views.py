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

# TEST ENDPOINT URL https://checkout.test.paycom.uz/api
# AUTHORIZATION X-Auth: {id}:{password}  
# Test page link https://developer.help.paycom.uz/protokol-subscribe-api


AUTHORIZATION = {'X-Auth': '{}:{}'.format(PAYME_SETTINGS['PAY_ME_ID'], PAYME_SETTINGS['PAY_ME_TEST_KEY'])}
URL = 'https://checkout.test.paycom.uz/api'


class CardsCheck(APIView):
    '''Проверяем токен пластиковокй карты от фронта'''
    
    def get(self, request):
        serializer = SubscribeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        result = self.cards_check(serializer.validated_data)
        
        return Response(result)
    
    def cards_check(self, validated_data):
        data = dict(
            # id=validated_data['id'],
            id='123456789',
            method='cards.verify',
            params=dict(
                token=validated_data['params']['token'],
            )
        )
        
        response = requests.get(URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        if 'error' in result:
            return result
        
        return result


@api_view(['GET', 'POST'])
def main(request):
    return HttpResponse('main')
    # if request.method == 'POST':
    #     return Response({"message": "Got some data!", "data": request.data})
    # return Response({"message": "Hello, world!"})


def index(request):
    return HttpResponse('Index')

