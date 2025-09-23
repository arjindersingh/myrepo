from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.employee import JobCategory

@receiver(post_migrate)
def populate_job_categories(sender, **kwargs):
    """Populates JobCategory with default values if they don't exist."""
    if sender.name == "accounts":  # 🔹 Replace with your actual app name
        DEFAULT_CATEGORIES = [
            ("1", "Teaching"),
            ("2", "Non-teaching"),
            ("3", "Administrative Staff"),
        ]

        for code, name in DEFAULT_CATEGORIES:
            JobCategory.objects.get_or_create(category_code=code, category_name=name)
