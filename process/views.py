from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})

def index(request):
    return HttpResponse('Hello')

# def main(request):
#     return HttpResponse('Main')