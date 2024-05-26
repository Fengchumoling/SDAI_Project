from django import forms
from django.contrib.auth.forms import UserCreationForm
from app1.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

# class UserLoginForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     name = forms.CharField(max_length=255)
#
#     class Meta:
#         model = User
#         fields = ['name', 'email', 'password1', 'password2']