from django.dispatch import receiver
from django.contrib.auth.models import Group
from accounts.models.menu import Menu, UserGroupMenuPermission
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Group)
def assign_default_menu_permissions(sender, instance, created, **kwargs):
    """Assign all menu permissions to a newly created group with can_access based on default_permission."""
    if created:
        menus = Menu.objects.all()
        for menu in menus:
            UserGroupMenuPermission.objects.create(group=instance, menu=menu, can_access=menu.default_permission)

@receiver(post_delete, sender=Group)
def delete_group_permissions(sender, instance, **kwargs):
    """Delete all menu permissions related to a deleted group."""
    UserGroupMenuPermission.objects.filter(group=instance).delete()