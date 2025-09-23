from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.employee import EmploymentStatus
from django.db import transaction


@receiver(post_migrate)
def add_employment_status(sender, **kwargs):
    if sender.name == "accounts":  # Replace with your actual app name
        statuses = ["Working", "Left", "Suspended"]
        
        with transaction.atomic():  # Ensures atomic DB operations
            for status in statuses:
                obj, created = EmploymentStatus.objects.get_or_create(name=status)
                if created:
                    print(f"Adding Employment Status: {status}")
                else:
                    print(f"Skipping Employment Status (already exists): {status}")
