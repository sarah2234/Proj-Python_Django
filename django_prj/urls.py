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
from django.urls import path
from apps.common.views import DashboardView, user_login, HomeView, update_profile
from django.contrib.auth import views as auth_views
# from apps.common.forms import register


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', HomeView.as_view(), name='home'),
    path('register/', update_profile, name='register'),
    
    path('login/', user_login, name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='dashboard'
        ),
        name='logout'
    ),
]

