from django import forms
from appraisal.models.domain import Domain

class DomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ['name', 'description', 'scale', 'acr_category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scale': forms.Select(attrs={'class': 'form-control'}),
            'acr_category': forms.Select(attrs={'class': 'form-control'}),
        }
