from django.shortcuts import render, redirect

from apps.common.forms import UserForm
from apps.userprofile.models import Profile

from django.contrib.auth import authenticate, login

app_name = 'time_table'


def update_profile(request):
    """
    계정생성
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile(user=user, student_ID=request.POST['student_ID'], CBNU_PW=request.POST['CBNU_PW']).save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('time_table:schedule')
    else:
        form = UserForm()
    return render(request, 'common/register.html', {'form': form})

