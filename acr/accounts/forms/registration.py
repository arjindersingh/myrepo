from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
User = get_user_model()


User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "password1": forms.PasswordInput(attrs={"placeholder": "Create a password"}),
            "password2": forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
        }

        labels = {
            "username": "Username",
            "email": "Email Address",
            "password1": "Password",
            "password2": "Confirm Password",
        }

        help_texts = {
            "username": "Required. Choose a unique username.",
            "password1": "Password must be at least 8 characters long and contain numbers & letters.",
            "password2": "Enter the same password again for confirmation.",
        }

        error_messages = {
            "username": {"required": "Username is required."},
            "email": {"required": "Email is required.", "invalid": "Enter a valid email address."},
            "password1": {"required": "Password is required."},
            "password2": {"required": "Please confirm your password."},
        }
