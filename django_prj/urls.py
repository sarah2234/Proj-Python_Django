"""django_prj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    
  from django.views.generic import TemplateView  
 path('', TemplateView.as_view(template_name='template.html')),

"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from apps.common.views import DashboardView, user_login, update_profile
from django.contrib.auth import views as auth_views

from django.views.generic import TemplateView
# from apps.common.forms import register


#원래 있던 urls.py 즉 login commit 하기 전거
# from django.contrib import admin
# from django.urls import path, include
# from django.views.generic import TemplateView

# urlpatterns = [
#     path('', TemplateView.as_view(template_name='template.html')),
#     path('time_table/', include('time_table.urls')),
#     path('admin/', admin.site.urls),
# ]

#path('', HomeView.as_view(), name='home'), 이거 삭제하고 templateview넣음

urlpatterns = [

    path('admin/', admin.site.urls),
    path('time_table/', include('time_table.urls')),
    path('', TemplateView.as_view(template_name='template.html')),
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('register/', update_profile, name='register'),
    
    path('login/', user_login, name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='dashboard'
        ),
        name='logout'
    ),
]
