from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.institute import Subject

@receiver(post_migrate)
def populate_subjects(sender, **kwargs):
    """
    Populates the database with common school subjects if they don't already exist.
    This runs after migrations are applied.
    """
    if sender.name == "accounts":  # Replace 'your_app' with your actual Django app name
        school_subjects = [
            {"subject_name": "Mathematics", "short_name": "Math", "description": "Covers algebra, geometry, trigonometry, and calculus."},
            {"subject_name": "English", "short_name": "Eng", "description": "Focuses on reading, writing, grammar, and literature."},
            {"subject_name": "Science", "short_name": "Sci", "description": "Includes physics, chemistry, and biology concepts."},
            {"subject_name": "Social Studies", "short_name": "SS", "description": "History, geography, civics, and economics."},
            {"subject_name": "Physics", "short_name": "Phy", "description": "Study of matter, energy, and forces."},
            {"subject_name": "Chemistry", "short_name": "Chem", "description": "Study of substances, their properties, and reactions."},
            {"subject_name": "Biology", "short_name": "Bio", "description": "Study of living organisms and their processes."},
            {"subject_name": "Computer Science", "short_name": "CS", "description": "Covers programming, algorithms, and computing basics."},
            {"subject_name": "Environmental Science", "short_name": "EVS", "description": "Study of the environment and sustainability."},
            {"subject_name": "Physical Education", "short_name": "PE", "description": "Covers sports, health, and fitness education."},
            {"subject_name": "Economics", "short_name": "Eco", "description": "Study of financial systems, markets, and economic policies."},
            {"subject_name": "Political Science", "short_name": "Pol Sci", "description": "Study of government, politics, and policies."},
            {"subject_name": "Psychology", "short_name": "Psy", "description": "Study of human behavior and mental processes."},
            {"subject_name": "Sociology", "short_name": "Soc", "description": "Study of society, culture, and human interactions."},
            {"subject_name": "Hindi", "short_name": "Hin", "description": "Study of Hindi language, literature, and grammar."},
            {"subject_name": "Punjabi", "short_name": "Punj", "description": "Study of Punjabi language, literature, and grammar."},
            {"subject_name": "Art & Craft", "short_name": "Art", "description": "Covers drawing, painting, and creativity."},
            {"subject_name": "Music", "short_name": "Music", "description": "Covers vocal and instrumental music education."},
            {"subject_name": "Moral Science", "short_name": "MSc", "description": "Covers ethics, values, and moral education."},
            {"subject_name": "Business Studies", "short_name": "BSt", "description": "Covers entrepreneurship and business management."},
            {"subject_name": "Accounts", "short_name": "Acc", "description": "Study of financial records and bookkeeping."},
            {"subject_name": "All Subjects", "short_name": "All", "description": "Teacher teaches All Subjects ."},
        ]

        for subject in school_subjects:
            Subject.objects.get_or_create(
                subject_name=subject["subject_name"],
                short_name=subject["short_name"],
                defaults={"description": subject["description"]}
            )
