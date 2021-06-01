from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from apps.userprofile.models import Profile

# from django.db.models import fields

# from django.db import models
# from django.shortcuts import render, redirect


# class SignUpForm(UserCreationForm):
#     first_name = forms.CharField(max_length=30, required=False, help_text='Optional',
#                                  widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
#     last_name = forms.CharField(max_length=30, required=False, help_text='Optional',
#                                 widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
#     email = forms.EmailField(max_length=254, required=False, help_text='Enter a valid email address',
#                              widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
#     student_ID = forms.CharField(max_length=30, required=False, help_text='Optional',
#                                  widget=forms.TextInput(attrs={'placeholder': 'student_ID'}))
#     CBNU_PW = forms.CharField(max_length=30, required=False, help_text='Optional',
#                               widget=forms.TextInput(attrs={'placeholder': 'CBNU_PW'}))
#
#     class Meta:
#         model = User
#         fields = [
#             'first_name',
#             'last_name',
#             'email',
#             'student_ID',
#             'CBNU_PW',
#         ]


class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "first_name", 'last_name', "email")

# class SignUpForm(UserCreationForm):
#
#     first_name = forms.CharField(max_length=30, required=False, help_text='Optional', widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
#     last_name = forms.CharField(max_length=30, required=False, help_text='Optional', widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
#     email = forms.EmailField(max_length=254, required=False, help_text='Enter a valid email address', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
#
#     class Meta:
#         model = User
#         widgets = {
#             'username': forms.TextInput(attrs={'placeholder': 'Username'})
#         }
#         fields = [
#             'username',
#             'first_name',
#             'last_name',
#             'email',
#         ]
#
# class ProfileForm(forms.ModelForm):
#
#     class Meta:
#         model = Profile
#         fields= [ 'student_ID', 'CBNU_PW' ]
#         widgets = {
#             'student_ID': forms.TextInput(attrs={'placeholder': 'student_ID'}),
#             'CBNU_PW': forms.TextInput(attrs={'placeholder': 'CBNU_PW'})
#         }
#
# def register(request):
#     form = SignUpForm()

#     if request.method=='POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             # assuming you have a Profile model with a OneToOne Field to User
#             user.save()
#             profile=Profile()
#             profile.user=user
#             profile.student_ID=request.POST["student_ID"]
#             profile.CBNU_PW=request.POST['CBNU_PW']
#             profile.save()
#             return redirect('login') 

#     context = {'form': form}          
#     return render(request, 'common/register.html', context)