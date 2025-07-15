from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('department/<str:pk>/', views.department, name="department"),
]