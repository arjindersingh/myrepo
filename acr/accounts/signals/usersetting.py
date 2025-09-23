# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from accounts.models.setting import Setting, UserSetting


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        for setting in Setting.objects.all():
            # Skip if user already has this setting
            if not UserSetting.objects.filter(user=instance, setting=setting).exists():
                UserSetting.objects.create(
                    user=instance,
                    setting=setting,
                    value=setting.default_value  # Store raw text, validation is handled in clean()
                )
