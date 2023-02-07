from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    path('cards/create/', views.CardsCreate.as_view()),
    path('api/verify/', views.CardVerify.as_view(), name='card_verify'),
    path('api/receipts/', views.Receipts.as_view()),
    # path('api/cards/verify', views.CardsVerify.as_view()),
    # path('api/cards/remove', views.CardsRemove.as_view()),
    # path('api/receipts', views.Receipts.as_view()),
]