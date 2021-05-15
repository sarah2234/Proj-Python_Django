from django.urls import path

from . import views

app_name = 'time_table'

urlpatterns = [
    path('', views.table, name='table'),
    path('crawling/', views.crawling, name='crawling'),
]