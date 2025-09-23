from django import forms
from appraisal.models.appraisal_type import AppraisalSchedule
from django.core.exceptions import ValidationError
from datetime import date

class AppraisalScheduleForm(forms.ModelForm):
    class Meta:
        model = AppraisalSchedule
        fields = ['start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select start date'
                }
            ),
            'end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select end date'
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter schedule description',
                    'maxlength': 200,  # ✅ max length for beautification
                }
            ),
        }
        labels = {
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'description': 'Description',
        }
        help_texts = {
            'description': 'Provide a short description (max 200 characters).',
        }


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not start_date:
            self.add_error('start_date', "Start date is required.")
        if not end_date:
            self.add_error('end_date', "End date is required.")

        if start_date and start_date < date.today():
            self.add_error('start_date', "Start date cannot be in the past.")

        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', "End date must be after start date.")

        return cleaned_data