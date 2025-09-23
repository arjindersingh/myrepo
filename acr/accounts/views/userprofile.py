from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.forms.userprofile import BasicUserProfileForm, ProUserProfileForm # FullUserProfileForm
from accounts.models.userprofile import UserProfile
from accounts.decorators import menu_permission_required
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.contrib.auth import password_validation

from accounts.forms.password_change import SimplePasswordChangeForm


def edit_basic_user_profile(request):
    """Allows the logged-in user to edit their own profile (personal info only)."""
    user_profile = request.user.profile  # Get the user's profile

    if request.method == "POST":
        form = BasicUserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("ShowDashboard")  # Redirect after successful update
        else:
            messages.error(request, "Please correct the errors below.")  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = BasicUserProfileForm(instance=user_profile)

    return render(request, "userprofile/edit_basic_profile.html", {"form": form})


@login_required
def edit_pro_user_profile(request, user_id):
    """
    Allows an administrator or authorized group to edit any user's professional information.
    """

    # ✅ Get User and related UserProfile (create if missing)
    user = get_object_or_404(User, id=user_id)
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    password_change_form = SimplePasswordChangeForm(request.POST)
    if request.method == "POST":
        if "update_user_profile" in request.POST:
            form = ProUserProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                # ✅ form.save() handles User + UserProfile + M2M
                form.save()
                messages.success(request, f"Profile for {user.username} updated successfully!")
                return redirect("list_user_profiles")
            else:
                messages.error(request, "Please correct the errors below.")

        if "change_password" in request.POST:
            password_change_form = SimplePasswordChangeForm(request.POST)
            if password_change_form.is_valid():
                new_pwd = password_change_form.cleaned_data["password1"]
                user.set_password(new_pwd)
                user.save()
                # keep the user logged in after password change
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                #return redirect("list_user_profiles")
            else:
                messages.error(request, "Please fix the errors below.")
    #else:
        # ✅ Prefill form (ProUserProfileForm __init__ handles username & email prefill)
    form = ProUserProfileForm(instance=user_profile)
    password_change_form = SimplePasswordChangeForm()
    # Collect condition strings to show as bullet points (optional – already in form help_text)
    validator_texts = [
        v.get_help_text() for v in password_validation.get_password_validators(
            settings.AUTH_PASSWORD_VALIDATORS
        )
    ]
    return render(
        request,
        "userprofile/edit_pro_profile.html",
        {
            "form": form,
            "user_profile": user_profile,
            "edit_user": user,
            "created": created,
            "password_change_form": password_change_form,
            "validator_texts": validator_texts,
        },
    )




@login_required
@menu_permission_required
def list_user_profiles(request):
    """List all users and allow profile creation or editing."""
    users = User.objects.all()  
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, "Your profile has been created. Please update your details.")

    """     if request.method == "POST":
        form = FullUserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("list_user_profiles")
    else:
        form = FullUserProfileForm(instance=user_profile) """

    return render(request, "userprofile/list.html", {
        "users": users,
        #"form": form,
        "user_profile": user_profile,
    })




""" 
@login_required
def password_change_using_profile(request):
    ""
    Shows a single 'New password' field and changes the user's password on submit.
    Uses Django's built-in validators defined in AUTH_PASSWORD_VALIDATORS.
    ""
    if request.method == "POST":
        password_change_form = SimplePasswordChangeForm(request.POST)
        if form.is_valid():
            new_pwd = form.cleaned_data["password1"]
            user = request.user
            user.set_password(new_pwd)
            user.save()
            # keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully.")
            return redirect("password_change_using_profile")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SimplePasswordChangeForm()

    # Collect condition strings to show as bullet points (optional – already in form help_text)
    validator_texts = [
        v.get_help_text() for v in password_validation.get_password_validators(
            settings.AUTH_PASSWORD_VALIDATORS
        )
    ]

    return render(request, "userprofile/edit_pro_profile.html", {
        "password_change_form": password_change_form,
        "validator_texts": validator_texts,
        "active_tab": "password",
    })
"""