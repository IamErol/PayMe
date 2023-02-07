from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    path('api/payinit', views.CardsCreate.as_view()),
    # path('api/cards/check', views.CardsCheck.as_view()),
    # path('api/cards/verify', views.CardsVerify.as_view()),
    # path('api/cards/remove', views.CardsRemove.as_view()),
    # path('api/receipts', views.Receipts.as_view()),
]