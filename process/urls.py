from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main/', views.main),
    # path('api/token', views.CardsCheck.as_view()),
    path('api/token', views.ab),
]