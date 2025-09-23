from django import forms
from appraisal.models.appraisal_type import AppraisalType
from appraisal.models.appraisal_type import AppraisalCategory


class AppraisalTypeForm(forms.ModelForm):
    class Meta:
        model = AppraisalType
        fields = '__all__'  # include all fields (including at_category)

        labels = {
            'name': 'Appraisal Name',
            'display_name': 'Display Name',
            'short_name': 'Short Code',
            'at_category': 'Appraisal Category',
            'at_job_categories': 'Applicable Job Categories',
            'at_institutes': 'Applicable Institutes',
            'at_departments': 'Applicable Departments',
            'at_wings': 'Applicable Wings',
            'at_subjects': 'Applicable Subjects',
            'app_emp_exclusion': 'Exclude Employees (Appraisal)',
            'inspection_emp_exclusion': 'Exclude Employees (Inspection)',
            'domain_name': 'Domain Name',
            'domain_description': 'Domain Description',
            'domain_weight': 'Domain Weight (%)',
            'scale': 'Rating Scale',
        }

        help_texts = {
            'name': 'Enter the internal name for this appraisal type.',
            'display_name': 'Enter the user-friendly name to display in the system.',
            'short_name': 'Provide a short code or abbreviation (e.g., “APT-01”).',
            'at_category': 'Select the category this appraisal type belongs to.',
            'at_job_categories': 'Select job categories this appraisal type applies to.',
            'at_institutes': 'Select institutes where this appraisal type is applicable.',
            'at_departments': 'Select departments for this appraisal type.',
            'at_wings': 'Select wings or divisions where it applies.',
            'at_subjects': 'Select subjects (if subject-based evaluation is needed).',
            'app_emp_exclusion': 'Mark this if employees should be excluded from the appraisal process.',
            'inspection_emp_exclusion': 'Mark this if employees should be excluded from the inspection process.',
            'domain_name': 'Enter the domain name related to this appraisal type.',
            'domain_description': 'Provide a short description for the domain.',
            'domain_weight': 'Assign weight to this domain (e.g., 30 for 30%).',
            'scale': 'Choose the rating scale (e.g., 1–5, 1–10).',
        }

        widgets = {
            'at_category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter appraisal type name'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter display name'
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter short code'
            }),
            'at_job_categories': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'at_institutes': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'at_departments': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'at_wings': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'at_subjects': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'app_emp_exclusion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'inspection_emp_exclusion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'domain_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter domain name'
            }),
            'domain_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter domain description',
                'rows': 3
            }),
            'domain_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter domain weight (e.g., 20)'
            }),
            'scale': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
