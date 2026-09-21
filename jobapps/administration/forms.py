from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserManagementForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['base_role', 'is_active']
        labels = {
            'base_role': 'Role',
            'is_active': 'Active Account',
        }