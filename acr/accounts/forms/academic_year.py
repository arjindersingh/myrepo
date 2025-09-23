from django import forms
from accounts.models.academicyear import AcademicYear

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = [
            'year_name', 'short_name', 'display_name',
            'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
