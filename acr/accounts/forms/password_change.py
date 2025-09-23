# accounts/forms.py
from django import forms
from django.contrib.auth import password_validation

class SimplePasswordChangeForm(forms.Form):
    password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "class": "form-control",
            "placeholder": "Enter new password"
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )

    def clean_password1(self):
        pwd = self.cleaned_data.get("password1")
        password_validation.validate_password(pwd)
        return pwd
