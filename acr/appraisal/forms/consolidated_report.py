from django import forms
from accounts.models.institute import Institute
from accounts.models.employee import JobCategory

class AppraisalConsolidatedReportForm(forms.Form):
    emp_institutes = forms.ModelMultipleChoiceField(
        queryset=Institute.objects.all().order_by("institute_name"),
        required=False,
        label="Institute(s)",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6})
    )
    emp_job_categories = forms.ModelMultipleChoiceField(
        queryset=JobCategory.objects.all().order_by("category_name"),
        required=False,
        label="Job Category(ies)",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6})
    )
