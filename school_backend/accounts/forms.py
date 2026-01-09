# forms.py (create this file in the same directory as admin.py)
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserCreationForm(UserCreationForm):
    """Custom user creation form for admin"""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

class UserChangeForm(UserChangeForm):
    """Custom user change form for admin"""
    
    class Meta:
        model = User
        fields = '__all__'