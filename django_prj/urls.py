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
from django.urls import path, include
from apps.common.views import update_profile
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', update_profile, name='register'),

    path('time_table/', include('time_table.urls'), name='time_table'),

    path('admin/', admin.site.urls),
]
