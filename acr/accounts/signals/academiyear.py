from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime
from accounts.models.academicyear import AcademicYear

@receiver(post_migrate)
def populate_academic_years(sender, **kwargs):
    if sender.name == "accounts":
        start_year = 2020
        end_year = datetime.now().year + 5
        current_date = timezone.now().date()  # Get today's date

        active_year_set = False  # Track if an active year is set

        for year in range(start_year, end_year):
            year_name = f"{year}-{year+1}"
            short_name = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
            display_name = f"AY {year}-{year+1}"
            start_date = timezone.make_aware(datetime(year, 4, 1))  # Start in April
            end_date = timezone.make_aware(datetime(year + 1, 3, 31))  # Ends in March next year

            # Determine if this should be the active academic year
            is_active = start_date.date() <= current_date <= end_date.date()

            if is_active:
                active_year_set = True  # Mark that an active year is set

            academic_year, created = AcademicYear.objects.get_or_create(
                year_name=year_name,
                defaults={
                    "short_name": short_name,
                    "display_name": display_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_active": is_active,  # Set active based on current date
                }
            )

             # If the record already exists, update its is_active status
            if not created and is_active:
                academic_year.is_active = True
                academic_year.save()

        # Ensure only one active academic year exists
        if active_year_set:
            AcademicYear.objects.exclude(year_name=year_name).update(is_active=False)
