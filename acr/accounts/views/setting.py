from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models.setting import Setting, UserSetting
from accounts.forms.setting import SettingForm, UserSettingsForm
from accounts.models.academicyear import AcademicYear
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import json
from typing import Dict, Any, Union

def setting_list(request):
    """Display all settings for the active academic year."""
    active_year = AcademicYear.get_active_academic_year()
    if not active_year:
        messages.error(request, "No active academic year found.")
        return redirect('/')

    settings = Setting.objects.filter(academic_year=active_year)
    return render(request, 'setting/list.html', {'settings': settings, 'active_year': active_year})

def setting_edit(request, setting_id):
    """Edit a specific setting."""
    setting = get_object_or_404(Setting, id=setting_id)
    
    if request.method == 'POST':
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Setting updated successfully!")
            return redirect('setting_list')
    else:
        form = SettingForm(instance=setting)

    return render(request, 'setting/edit.html', {'form': form, 'setting': setting})



def update_user_settings(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Step 1: Get all settings
    all_settings = Setting.objects.all()

    # Step 2: Build list with either user-specific value or default
    settings_data = []
    for setting in all_settings:
        try:
            user_setting = UserSetting.objects.get(user=user, setting=setting)
            current_value = user_setting.value
        except UserSetting.DoesNotExist:
            user_setting = None
            current_value = setting.default_value

        settings_data.append({
            'setting': setting,
            'user_setting': user_setting,
            'current_value': current_value,
        })

    # Step 3: Handle POST request
    if request.method == 'POST':
        for item in settings_data:
            setting = item['setting']
            field_name = f'setting_{setting.id}'
            new_value = request.POST.get(field_name)

            if new_value is None:
                continue  # Skip if no input

            # Update existing record or create new one
            if item['user_setting']:
                usersetting = item['user_setting']
                usersetting.value = new_value
            else:
                usersetting = UserSetting(user=user, setting=setting, value=new_value)

            try:
                usersetting.clean()  # Validate against type
                usersetting.save()
            except ValidationError as e:
                messages.error(request, f"Error in setting '{setting.name}': {e}")
                continue

        messages.success(request, f"Settings updated for {user.username}!")
        return redirect('update_user_settings', user_id=user.id)

    # Step 4: Render template
    return render(request, 'setting/update_user_settings.html', {
        'user': user,
        'settings_data': settings_data,
    })