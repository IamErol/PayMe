from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def getRoutes(request):
    
    routes = [
        {'GET': 'process/urls'}
    ]
    
    return Response(routes)

def index(request):
    return HttpResponse('Hello')