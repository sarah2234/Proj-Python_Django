from django.urls import path

from . import views

app_name = 'time_table'

urlpatterns = [
    path('load/', views.load, name='load'),
    # 학번, 비번 입력받고 블랙보드 공지사항 읽어오는 곳. 간단하게 확인가능
    path('crawling/', views.crawling, name='crawling'),
    path('', views.schedule, name='schedule')
]