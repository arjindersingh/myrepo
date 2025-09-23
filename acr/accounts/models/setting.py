from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json

SETTING_TYPE_CHOICES = [
    ('string', 'String'),
    ('number', 'Number'),
    ('boolean', 'Boolean'),
    ('json', 'JSON'),
]

class Setting(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Setting name (e.g., enable_online_classes)"
    )
    display_name = models.CharField(
        max_length=100,
        default = "",
        help_text="Human-readable name for display (e.g., Enable Online Classes)"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the setting’s purpose or usage"
    )
    setting_type = models.CharField(
        max_length=10,
        choices=SETTING_TYPE_CHOICES
    )
    default_value = models.TextField(
        help_text="Stores value based on type (JSON for structured data)"
    )
    def clean(self):
        """Validate that the default_value matches the setting_type"""
        try:
            self.get_typed_value(self.default_value)
        except (ValueError, json.JSONDecodeError) as e:
            raise ValidationError(f"Invalid default_value for type {self.setting_type}: {str(e)}")
    
    def get_typed_value(self, value):
        """Convert text value to proper Python type based on setting_type"""
        if self.setting_type == 'string':
            return str(value)
        elif self.setting_type == 'number':
            return float(value)
        elif self.setting_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1')
            return bool(value)
        elif self.setting_type == 'json':
            if isinstance(value, str):
                return json.loads(value)
            return value
        return value
    
    def __str__(self):
        return f"{self.name} ({self.setting_type})"

class UserSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_settings")
    setting = models.ForeignKey('Setting', on_delete=models.CASCADE, related_name="user_specific_settings")
    value = models.TextField(help_text="User-specific value, overrides global setting if present")
    
    class Meta:
        unique_together = ('user', 'setting')
    
    def clean(self):
        """Validate that the value matches the setting's type"""
        try:
            self.setting.get_typed_value(self.value)
        except (ValueError, json.JSONDecodeError) as e:
            raise ValidationError(f"Invalid value for type {self.setting.setting_type}: {str(e)}")
    
    def get_typed_value(self):
        """Get the properly typed value"""
        return self.setting.get_typed_value(self.value)
    @classmethod
    def get_user_setting(cls, user_or_request, setting_name):
        """
        Fetch user-specific setting value, or default if not found.
        :param user_or_request: Either a User instance or a request object
        :param setting_name: The 'name' field from Setting
        """
        # Get user instance from request or directly
        if hasattr(user_or_request, "user"):
            user = user_or_request.user
        else:
            user = user_or_request

        # Get the Setting instance
        try:
            setting_obj = Setting.objects.get(name=setting_name)
        except Setting.DoesNotExist:
            raise ObjectDoesNotExist(f"Setting '{setting_name}' does not exist.")

        # Try to get UserSetting
        try:
            user_setting = cls.objects.get(user=user, setting=setting_obj)
            return user_setting.get_typed_value()
        except cls.DoesNotExist:
            # Return the default value from Setting
            return setting_obj.get_typed_value(setting_obj.default_value)
    def __str__(self):
        return f"{self.user.username}'s setting for {self.setting.name}"