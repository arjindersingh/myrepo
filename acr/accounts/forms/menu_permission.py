from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models.menu import UserGroupMenuPermission

class UserGroupMenuPermissionForm(forms.ModelForm):
    class Meta:
        model = UserGroupMenuPermission
        fields = ['can_access']
        widgets = {
            'can_access': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }