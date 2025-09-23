from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.institute import Wing

@receiver(post_migrate)
def create_default_wings(sender, **kwargs):
    # List of predefined wings to populate
    wings_data = [
        ("Pre Primary", "Wing for children in early education before primary school."),
        ("Primary", "Wing for children in the primary phase of education."),
        ("Middle", "Wing for children in the middle phase of education."),
        ("Higher", "Wing for children in the higher phase of education."),
        ("Senior Secondary", "Wing for students in the senior secondary phase.")
    ]
    
    # Loop through each predefined wing and create it if it doesn't exist
    for name, description in wings_data:
        Wing.objects.get_or_create(name=name, description=description)

