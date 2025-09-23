# forms.py
from django import forms

class EmployeeBulkUploadForm(forms.Form):
    csv_file = forms.FileField(help_text="Upload a CSV with employees.")
    dry_run = forms.BooleanField(required=False, initial=True, help_text="Validate only, no database writes.")
    update_existing = forms.BooleanField(required=False, initial=True, help_text="Update if emp_code already exists.")
    create_missing_related = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Create missing related objects (JobCategory/Institute/etc.) if not found by name."
    )
    delimiter = forms.ChoiceField(
        choices=[(",", "Comma ,"), ("|", "Pipe |")],
        initial=",",
        help_text="How values in multi-value cells are separated."
    )
