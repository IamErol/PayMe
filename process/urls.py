from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    path('api/card/create', views.CardsCheck.as_view()),
    path('api/card/remove', views.CardsRemove.as_view()),
    path('api/receipts', views.Receipts.as_view()),
    
]