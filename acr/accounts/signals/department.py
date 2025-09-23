from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.institute import Department

@receiver(post_migrate)
def populate_departments(sender, **kwargs):
    """
    Populates the database with predefined department names if they don't already exist.
    This runs after migrations are applied.
    """
    if sender.name == "accounts":  # Replace 'your_app' with your actual Django app name
        default_departments = [
            {"department_name": "Mathematics", "short_name": "Maths"},
            {"department_name": "Science", "short_name": "SCI"},
            {"department_name": "Physics", "short_name": "PHY"},
            {"department_name": "Chemistry", "short_name": "CHEM"},
            {"department_name": "Biology", "short_name": "BIO"},
            {"department_name": "Computer Science", "short_name": "CS"},
            {"department_name": "English", "short_name": "ENG"},
            {"department_name": "Hindi", "short_name": "HIN"},
            {"department_name": "Social Science", "short_name": "SST"},
            {"department_name": "History", "short_name": "HIST"},
            {"department_name": "Political Science", "short_name": "PS"},
            {"department_name": "Geography", "short_name": "GEO"},
            {"department_name": "Economics", "short_name": "ECO"},
            {"department_name": "Commerce", "short_name": "COM"},
            {"department_name": "Fine Arts", "short_name": "FA"},
            {"department_name": "Performing Arts", "short_name": "PA"},
            {"department_name": "Physical Education", "short_name": "PE"},
            {"department_name": "Sports", "short_name": "SPORTS"},
            {"department_name": "Library", "short_name": "LIB"},
        ]


        for dept in default_departments:
            Department.objects.get_or_create(
                department_name=dept["department_name"],
                short_name=dept["short_name"]
            )

