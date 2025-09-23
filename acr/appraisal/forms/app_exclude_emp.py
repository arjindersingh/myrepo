from django import forms
from appraisal.models.app_excluded_emp import AppExcludedEmp
from accounts.models.employee import Employee
from appraisal.models.appraisal_type import AppraisalType
from django.core.exceptions import ValidationError

class AppExcludedEmpCreateForm(forms.ModelForm):
    appraisal_type = forms.ModelChoiceField(
        queryset=AppraisalType.objects.none(),   # set in __init__
        required=True,
        label="Appraisal Type",
        help_text="Select the appraisal type for which the employee should be excluded."
    )
    # Filled by your JS lookup; hidden to avoid loading entire employee list
    ex_employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),        # set in __init__ (lightweight)
        widget=forms.HiddenInput,
        required=True,
        label="Employee"
    )
    description = forms.CharField(
        required=False,
        label="Notes (optional)",
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "Reason or notes for exclusion (optional)…",
        }),
        help_text="Add a short note for future reference."
    )

    class Meta:
        model = AppExcludedEmp
        fields = ["appraisal_type", "ex_employee", "description"]
        widgets = {
            "appraisal_type": forms.Select(attrs={"aria-label": "Appraisal Type"}),
        }
        labels = {
            "ex_employee": "Employee",
        }
 
    def __init__(self, *args, **kwargs):
        """
        Pass current_user and current_ay from the view:
            form = AppExcludedEmpCreateForm(request.POST or None,
                                            current_user=request.user,
                                            current_ay=cay)
        """
        self.current_user = kwargs.pop("current_user", None)
        self.current_ay = kwargs.pop("current_ay", None)
        super().__init__(*args, **kwargs)

        # Dropdown queryset & ordering
        #self.fields["appraisal_type"].queryset = AppraisalType.objects.all().order_by("name" if hasattr(AppraisalType, "name") else "id")
        self.fields["appraisal_type"].queryset = (
            AppraisalType.objects
            #.filter(app_emp_exclusion=True)   # ✅ only those with exclusion enabled
            .order_by("name" if hasattr(AppraisalType, "name") else "id")
            )

        self.fields["appraisal_type"].empty_label = "— Select appraisal type —"

        # Keep employee queryset light; we only need to validate the chosen ID
        self.fields["ex_employee"].queryset = Employee.objects.all().only("id")
        # Restrict employees by institutes linked to user profile
        """         if self.current_user and hasattr(self.current_user, "userprofile"):
            allowed_institutes = self.current_user.userprofile.app_institutes.all()
            self.fields["ex_employee"].queryset = Employee.objects.filter(
                institute__in=allowed_institutes
            ).only("id")
        else:
            self.fields["ex_employee"].queryset = Employee.objects.none() """
        # Add nice classes/placeholders (Bootstrap-friendly)
        self.fields["appraisal_type"].widget.attrs.update({"class": "form-select"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})

        # Hidden field still needs an id for JS to target
        self.fields["ex_employee"].widget.attrs.update({"id": "id_ex_employee"})

    def clean_ex_employee(self):
        emp = self.cleaned_data.get("ex_employee")
        if not emp:
            raise ValidationError("Please select an employee from the search results.")
        return emp

    def clean(self):
        cleaned = super().clean()
        emp = cleaned.get("ex_employee")
        apptype = cleaned.get("appraisal_type")

        # Validate we received context from the view
        if not self.current_user or not self.current_ay:
            raise ValidationError("Internal error: user or academic year not provided.")

        # Prevent duplicates BEFORE hitting DB unique_together constraint
        if emp and apptype:
            exists = AppExcludedEmp.objects.filter(
                user=self.current_user,
                academic_year=self.current_ay,
                appraisal_type=apptype,
                ex_employee=emp,
            ).exists()
            if exists:
                raise ValidationError("This employee is already excluded for the selected appraisal type in the current academic year.")

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.user = self.current_user
        obj.academic_year = self.current_ay
        if commit:
            obj.save()
        return obj