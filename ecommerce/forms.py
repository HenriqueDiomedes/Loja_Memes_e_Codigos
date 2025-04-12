from django import forms
from .models import Administrador

class FormLogin(forms.Form):
    email = forms.EmailField(label='E-mail')
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput)