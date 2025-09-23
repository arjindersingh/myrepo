from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models.userprofile import UserProfile



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically creates a UserProfile when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves UserProfile whenever User is saved."""
    instance.profile.save()



