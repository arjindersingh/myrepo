from django import forms
from django.core.validators import MaxValueValidator
from accounts.models.employee import Employee
from accounts.models.employee import JobCategory, JobPost, EmploymentStatus
from accounts.models.institute import Institute, Department,  Subject, Wing 


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "emp_code",
            "emp_name",
            "employment_status",
            "job_categories",
            "institutes",
            "departments",
            "teaching_posts",
            "subjects",
            "wings",
        ]

        # Use SelectMultiple for M2M; keep FK as Select
        widgets = {
            "emp_code": forms.NumberInput(attrs={"class": "form-control"}),
            "emp_name": forms.TextInput(attrs={"class": "form-control"}),
            "employment_status": forms.Select(attrs={"class": "form-select"}),
            "job_categories": forms.CheckboxSelectMultiple(),
            "institutes": forms.CheckboxSelectMultiple(),
            "departments": forms.CheckboxSelectMultiple(),
            "teaching_posts": forms.CheckboxSelectMultiple(),
            "subjects": forms.CheckboxSelectMultiple(),
            "wings": forms.CheckboxSelectMultiple(),
        }

        labels = {
            "emp_code": "Employee Code",
            "emp_name": "Employee Name",
            "employment_status": "Employment Status",
            "job_categories": "Job Categories",
            "institutes": "Institutes",
            "departments": "Departments",
            "teaching_posts": "Teaching Posts",
            "subjects": "Subjects",
            "wings": "Wings",
        }

        help_texts = {
            "emp_code": "Card number up to 99999.",
            "employment_status": "Select the current status (e.g., Working).",
            "job_categories": "Hold Ctrl/Cmd to select multiple options.",
            "institutes": "Select all institutes associated with the employee.",
            "departments": "Select all relevant departments.",
            "teaching_posts": "Add all applicable teaching posts.",
            "subjects": "Choose all subjects taught.",
            "wings": "Pick one or more wings (primary, senior, etc.).",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Read-only emp_code when editing
        if self.instance and self.instance.pk:
            self.fields["emp_code"].widget.attrs["readonly"] = True
            # Optional: visually indicate read-only
            self.fields["emp_code"].widget.attrs["style"] = "background:#f8f9fa;"

        # Sort dropdowns for better UX
        self.fields["employment_status"].queryset = EmploymentStatus.objects.all().order_by("name")
        self.fields["job_categories"].queryset = JobCategory.objects.all().order_by("category_name")
        self.fields["institutes"].queryset = Institute.objects.all().order_by("institute_name")
        self.fields["departments"].queryset = Department.objects.all().order_by("department_name")
        self.fields["teaching_posts"].queryset = JobPost.objects.all().order_by("post_name")
        self.fields["subjects"].queryset = Subject.objects.all().order_by("subject_name")
        self.fields["wings"].queryset = Wing.objects.all().order_by("name")

        # Nice empty label for FK
        self.fields["employment_status"].empty_label = "— Select Status —"

        # Add consistent Bootstrap classes if needed
        # (Already set in widgets, but this ensures any future fields also look good)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, (forms.TextInput, forms.NumberInput)):
                w.attrs.setdefault("class", "form-control")
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault("class", "form-select")

    def clean_emp_code(self):
        value = self.cleaned_data.get("emp_code")
        if value is not None and value > 99999:
            raise forms.ValidationError("Employee code must be ≤ 99999.")
        return value
