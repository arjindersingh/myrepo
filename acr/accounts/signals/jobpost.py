from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.employee import JobPost, JobCategory

@receiver(post_migrate)
def create_default_job_posts(sender, **kwargs):
    if sender.name == "accounts":  # Replace 'your_app' with your actual app name

        default_job_posts = [
            # Teaching Posts
            {"post_name": "PRT", "short_name": "PRT", "display_name": "Primary Teacher", "description": "Primary School Teacher (Class 1-5)"},
            {"post_name": "TGT", "short_name": "TGT", "display_name": "Trained Graduate Teacher", "description": "Middle School Teacher (Class 6-10)"},
            {"post_name": "PGT", "short_name": "PGT", "display_name": "Post Graduate Teacher", "description": "Senior Secondary Teacher (Class 11-12)"},
            {"post_name": "NTT", "short_name": "NTT", "display_name": "Nursery Teacher", "description": "Pre-Primary & Nursery Level Teacher"},
            {"post_name": "Assistant Teacher", "short_name": "AsstT", "display_name": "Assistant Teacher", "description": "Supports Main Subject Teacher"},
            
            # Special Teaching Roles
            {"post_name": "Librarian", "short_name": "LIB", "display_name": "Librarian", "description": "Manages Library & Books"},

            # Coaching & Training Staff
            {"post_name": "Coach", "short_name": "Coach", "display_name": "Sports Coach", "description": "Provides Coaching for Sports"},

            # Administrative & Non-Teaching Roles
            {"post_name": "Principal", "short_name": "Prin", "display_name": "Principal", "description": "Head of the School"},
            {"post_name": "Vice Principal", "short_name": "VP", "display_name": "Vice Principal", "description": "Assists Principal in Management"},
            {"post_name": "Head of Department", "short_name": "HOD", "display_name": "HOD", "description": "Departmental Head"},
            {"post_name": "Clerk", "short_name": "Clerk", "display_name": "Office Clerk", "description": "Handles School Records & Admin Work"},
            {"post_name": "Receptionist", "short_name": "Recp", "display_name": "Receptionist", "description": "Front Desk Operations"},
            {"post_name": "IT Support", "short_name": "IT", "display_name": "IT Support Staff", "description": "Handles Computers & Network"},
            {"post_name": "Lab Assistant", "short_name": "LabAsst", "display_name": "Lab Assistant", "description": "Manages Science & Computer Labs"},
        ]

        # Get or create job categories
        teaching_category, _ = JobCategory.objects.get_or_create(name="Teaching")
        non_teaching_category, _ = JobCategory.objects.get_or_create(name="Non-Teaching")

        for job in default_job_posts:
            category = teaching_category if "Teacher" in job["display_name"] or job["post_name"] in ["PRT", "TGT", "PGT", "NTT"] else non_teaching_category
            obj, created = JobPost.objects.get_or_create(
                category=category,
                post_name=job["post_name"],
                defaults={
                    "short_name": job["short_name"],
                    "display_name": job["display_name"],
                    "description": job["description"]
                }
            )
            if created:
                print(f"✅ Created JobPost: {obj.display_name}")
            else:
                print(f"⚠️ Skipped (Already Exists): {obj.display_name}")

        print("🎉 JobPost seeding completed!")
