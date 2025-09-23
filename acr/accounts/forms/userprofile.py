from django import forms
from accounts.models.userprofile import UserProfile
from django.core.exceptions import ValidationError
from accounts.models.employee import Employee  # Import Employee model


class BasicUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "gender", "dob", "mobile", "emp_code"]

        widgets = {
            "display_name": forms.TextInput(),
            "gender": forms.Select(),
            "dob": forms.DateInput(attrs={"type": "date"}),
            "mobile": forms.TextInput(),
            "emp_code": forms.NumberInput(),
        }


    def clean_emp_code(self):
        emp_code = self.cleaned_data.get("emp_code")
        if not emp_code:
            raise ValidationError("Employee Code is required.")
        if not Employee.objects.filter(emp_code=emp_code).exists():
            raise ValidationError("Invalid Employee Code. Please enter a valid code assigned by your organization.")
        return emp_code




# 🔹 Common validation mixin
class EmpCodeValidationMixin:
    def clean_emp_code(self):
        emp_code = self.cleaned_data.get("emp_code")
        if not emp_code:
            raise ValidationError("Employee Code is required.")
        if not Employee.objects.filter(emp_code=emp_code).exists():
            raise ValidationError(
                "Invalid Employee Code. Please enter a valid code assigned by your organization."
            )
        return emp_code


# 🔹 Pro form
class ProUserProfileForm(EmpCodeValidationMixin, forms.ModelForm):
    # Extra fields from User model
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email"})
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter username"})
    )

    class Meta:
        model = UserProfile
        exclude = ["user"]   # 👈 don’t expose user FK in form

        labels = {
            "display_name": "Display Name",
            "gender": "Gender",
            "dob": "Date of Birth",
            "mobile": "Mobile Number",
            "emp_code": "Employee Code",

            "user_groups": "User Groups",
            "user_institutes": "User Institutes",
            "user_departments": "User Departments",
            "user_wings": "User Wings",
            "user_subjects": "User Subjects",

            "app_categories": "Appraisal Categories",
            "app_institutes": "Appraisal Institutes",
            "app_departments": "Appraisal Departments",
            "app_wings": "Appraisal Wings",
            "app_types": "Appraisal Domains",
            "app_subjects": "Appraisal Subjects",

            "inspection_categories": "Inspection Categories",
            "inspection_institutes": "Inspection Institutes",
            "inspection_departments": "Inspection Departments",
            "inspection_wings": "Inspection Wings",
            "inspection_types": "Inspection Domains",
            "inspection_subjects": "Inspection Subjects",
        }

        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "9876543210"}),
            "emp_code": forms.NumberInput(attrs={"class": "form-control"}),

            # User-related
            "user_groups": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "user_institutes": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "user_departments": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "user_wings": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "user_subjects": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),

            # Appraisal
            "is_assessor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "app_categories": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "app_institutes": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "app_departments": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "app_wings": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "app_types": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "app_subjects": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),

            # Inspection
            "is_inspector": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "inspection_categories": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "inspection_institutes": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "inspection_departments": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "inspection_wings": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "inspection_types": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "inspection_subjects": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["email"].initial = self.instance.user.email
            self.fields["username"].initial = self.instance.user.username
            self.fields["username"].widget.attrs["readonly"] = True
            self.fields["email"].widget.attrs["readonly"] = True

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if mobile and (not mobile.isdigit() or not 10 <= len(mobile) <= 15):
            raise forms.ValidationError("Enter a valid mobile number (10–15 digits).")
        return mobile

    def save(self, commit=True):
        instance = super().save(commit=False)

        # ✅ Update related User model fields
        if "email" in self.cleaned_data:
            instance.user.email = self.cleaned_data["email"]
        if "username" in self.cleaned_data:
            instance.user.username = self.cleaned_data["username"]
        instance.user.save()

        # ✅ Default display_name
        if not instance.display_name:
            instance.display_name = instance.user.username

        if commit:
            instance.save()
            self.save_m2m()

            # ✅ Clear appraisal M2M if assessor is unchecked
            if not instance.is_assessor:
                instance.app_categories.clear()
                instance.app_institutes.clear()
                instance.app_departments.clear()
                instance.app_wings.clear()
                instance.app_types.clear()
                instance.app_subjects.clear()

            # ✅ Clear inspection M2M if inspector is unchecked
            if not instance.is_inspector:
                instance.inspection_categories.clear()
                instance.inspection_institutes.clear()
                instance.inspection_departments.clear()
                instance.inspection_wings.clear()
                instance.inspection_types.clear()
                instance.inspection_subjects.clear()

        return instance
