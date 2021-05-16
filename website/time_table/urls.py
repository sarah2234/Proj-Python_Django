from django.urls import path

from . import views

app_name = 'time_table'

urlpatterns = [
    path('', views.table, name='table'),
    # 학번, 비번 입력받고 블랙보드 공지사항 읽어오는 곳. 간단하게 확인가능
    path('crawling/', views.crawling, name='crawling'),
    # template 적용. 알기쉽게 확인
    path('design1/', views.list_schedule, name='list_schedule'),
    path('design2/', views.weekly_schedule, name='weekly_schedule'),
]