import json
from django import forms
from accounts.models.setting import Setting, UserSetting


class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = ['default_value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget based on setting type
        if self.instance.setting_type == 'boolean':
            self.fields['default_value'].widget = forms.Select(choices=[('True', 'True'), ('False', 'False')])
        elif self.instance.setting_type == 'number':
            self.fields['default_value'].widget = forms.NumberInput()
        else:
            self.fields['default_value'].widget = forms.Textarea()





class UserSettingsForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Get all settings and create appropriate fields
        for setting in Setting.objects.all():
            field_name = setting.name
            initial_value = self.get_initial_value(setting)
            
            if setting.setting_type == 'string':
                self.fields[field_name] = forms.CharField(
                    initial=initial_value,
                    label=setting.name.replace('_', ' ').title(),
                    required=False
                )
            elif setting.setting_type == 'number':
                self.fields[field_name] = forms.FloatField(
                    initial=initial_value,
                    label=setting.name.replace('_', ' ').title(),
                    required=False
                )
            elif setting.setting_type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    initial=initial_value,
                    label=setting.name.replace('_', ' ').title(),
                    required=False
                )
            elif setting.setting_type == 'json':
                self.fields[field_name] = forms.JSONField(
                    initial=initial_value,
                    label=setting.name.replace('_', ' ').title(),
                    required=False
                )
    
    def get_initial_value(self, setting):
        """Get the initial value for a setting (user's value if exists, else default)"""
        try:
            user_setting = UserSetting.objects.get(user=self.user, setting=setting)
            return setting.get_typed_value(user_setting.value)
        except UserSetting.DoesNotExist:
            return setting.get_typed_value(setting.default_value)
    
    def save(self):
        """Save all user settings from the form"""
        for setting in Setting.objects.all():
            field_name = setting.name
            if field_name in self.cleaned_data:
                value = self.cleaned_data[field_name]
                self.save_setting(setting, value)
    
    def save_setting(self, setting, value):
        """Save or update a single user setting"""
        # Convert value to string for storage
        if setting.setting_type == 'json':
            str_value = json.dumps(value)
        else:
            str_value = str(value)
        
        # Update or create the UserSetting
        UserSetting.objects.update_or_create(
            user=self.user,
            setting=setting,
            defaults={'value': str_value}
        )