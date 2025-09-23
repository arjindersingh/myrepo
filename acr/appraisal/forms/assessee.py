from django import forms
from appraisal.models.assessee import AppraisalType
from appraisal.models.domain import Domain

class AssesseeFilterForm(forms.Form):
    acr_scheme = forms.ModelChoiceField(
        queryset=AppraisalType.objects.all(),
        required=False,
        label="Filter by ACR Scheme",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        label="Search Employee",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search Employee'})
    )
