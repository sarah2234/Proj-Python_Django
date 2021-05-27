from django.urls import path

from . import views

app_name = 'time_table'

urlpatterns = [
    path('load/', views.load, name='load'),
    # 학번, 비번 입력받고 블랙보드 공지사항 읽어오는 곳. 간단하게 확인가능
    path('crawling/', views.crawling, name='crawling'),
    path('', views.schedule, name='schedule'),
    path('setting', views.setting, name='setting'),
    path('cieat', views.cieat, name='cieat'),
    path('add_schedule', views.add_schedule, name='add_schedule'),
    path('add_schedule/add', views.add_function, name='add_function'),
    path('edit_schedule/<int:data_id>', views.edit_schedule, name='edit_schedule'),
    path('edit_schedule/<int:data_id>/delete', views.delete_function, name='delete_function'),
    path('edit_schedule/<int:data_id>/edit', views.edit_function, name='edit_function'),
]