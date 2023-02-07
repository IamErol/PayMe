from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    # path('api/cards/check', views.CardsCheck.as_view()),
    # path('api/cards/remove', views.CardsRemove.as_view()),
    # path('api/receipts', views.Receipts.as_view()),
    path('api/cards/create', views.CardsCreate.as_view()),
]