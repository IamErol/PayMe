from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    path('cards/create/', views.CardsCreate.as_view()),
    path('api/verify/', views.CardVerify.as_view(), name='card_verify'),
    path('api/receiptsget/', views.ReceiptsGet.as_view(), name='receipts_get'),

]