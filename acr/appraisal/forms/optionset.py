from django import forms
from appraisal.models.scale import OptionSet

class OptionSetForm(forms.ModelForm):
    class Meta:
        model = OptionSet
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Option Set Name'})
        }
