from django import forms
from appraisal.models.scale import Option

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'value']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Option Text'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Option Value'}),
        }
