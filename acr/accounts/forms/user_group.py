from django import forms
from django.contrib.auth.models import Group

# Form for creating/editing groups
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']  # Group only needs a 'name' field
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter group name'}),
        }
