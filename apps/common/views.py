from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, ProfileForm
from django.urls import reverse_lazy
  
# from .models import *
# from django.contrib import messages


# class DashboardView(TemplateView):
#     template_name = 'common/dashboard.html'
#     login_url = reverse_lazy('login')


from django.contrib.auth import authenticate, login

app_name = 'time_table'


def update_profile(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        print(form)
        print(profile_form)
        if form.is_valid() and profile_form.is_valid():
            print('생성')
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            
            profile.save()
            # username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(request, username=username, password=password)
            return redirect('login')

    else:
        form = SignUpForm()
        profile_form = ProfileForm()
    
    context = {'form': form, 'profile_form': profile_form}
    return render(request, 'common/register.html', context)


# def register(request):
#     form = SignUpForm()

#     if request.method=='POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             return redirect('login') 

#     context = {'form': form}          
#     return render(request, 'common/register.html', context)    


def user_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('time_table:schedule')
        else:
            return render(request, 'common/login.html', {'error' : 'username or password is incorrect.'})
    else:
        return render(request, 'common/login.html')


    
