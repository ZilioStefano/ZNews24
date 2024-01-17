from django.urls import path
from OcchioAggiro import views


urlpatterns = [
    path('', views.main, name='main'),
]