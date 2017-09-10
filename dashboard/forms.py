from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, PasswordChangeForm, \
    SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML, Submit
from .models import *

class LoginForm(AuthenticationForm):
    """Form to allow user to log in to system"""
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'name': 'password',
                                          'type': 'password'}))


class SignUpForm(UserCreationForm, PasswordResetForm):
    username = forms.CharField(
        label="Username",
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'username'}))
    password1 = forms.CharField(
        label="Password",
        max_length=30, strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'name': 'password',
                   'type': 'password'}))
    password2 = forms.CharField(
        label="Password confirmation",
        strip=False,
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'name': 'password confirmation',
                   'type': 'password'}))
    email = forms.CharField(
        label="email address",
        max_length=60,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'email address'}))

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']


class ChangePassword(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.helper = password_change_helper
        self.use_required_attribute = False

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']