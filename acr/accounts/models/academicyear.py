from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class AcademicYear(models.Model):
    year_name = models.CharField(max_length=20, unique=True, help_text="e.g., 2024-2025")
    short_name = models.CharField(max_length=10, unique=True, help_text="e.g., 24-25")
    display_name = models.CharField(max_length=50, help_text="e.g., Academic Year 2024-25")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ["-start_date"]

    def clean(self):
        """Ensure valid date range and enforce a single active academic year."""
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before the end date.")

    def save(self, *args, **kwargs):
        """Ensure only one active academic year at a time."""
        if self.is_active:
            AcademicYear.objects.filter(is_active=True).update(is_active=False)  # Deactivate others
        super().save(*args, **kwargs)

    @classmethod
    def get_active_academic_year(cls):
        """
        Returns the current active academic year (is_active=True).
        If no active year is found, returns the year where the current date is between start_date and end_date.
        Returns None if no suitable year is found.
        """
        # First, try to get the active academic year
        active_year = cls.objects.filter(is_active=True).first()
        if active_year:
            return active_year
        
        # If no active year, check for a year where current date is between start_date and end_date
        current_date = timezone.now()
        return cls.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()