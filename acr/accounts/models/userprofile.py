from django.db import models
from django.contrib.auth.models import User, Group
from accounts.models.employee import JobCategory
from accounts.models.institute import Institute, Department, Subject, Wing
from appraisal.models.appraisal_type import AppraisalType
#from appraisal.models.domain import Domain
from django.core.validators import MaxValueValidator, MinLengthValidator, RegexValidator

from home.choices import GENDER_CHOICES

#user.profile.user.employee.institute  # Fetch institute via Employee
#user.profile.user.employee.department  # Fetch department
#user.profile.user.employee.subject  # Fetch subject

class UserProfile(models.Model):
    """Extends User model to store additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Display Name")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    mobile = models.CharField(
        max_length=15,
        null=True, blank=True,
        validators=[RegexValidator(r'^\d{10,15}$', "Enter a valid mobile number (10-15 digits).")],
        verbose_name="Mobile"
    )
    emp_code = models.PositiveIntegerField(
        unique=True,
        validators=[MaxValueValidator(99999)],
        null=True, blank=True,
        verbose_name="Employee Code"
    )

    # User groups
    user_groups = models.ManyToManyField(Group, blank=True, verbose_name="User Groups")

    # User-related
    user_institutes = models.ManyToManyField(Institute, blank=True, related_name="userprofile_institutes")
    user_departments = models.ManyToManyField(Department, blank=True, related_name="userprofile_departments")
    user_wings = models.ManyToManyField(Wing, blank=True, related_name="userprofile_wings")
    user_subjects = models.ManyToManyField(Subject, blank=True, related_name="userprofile_subjects", verbose_name="User Subjects")

    # Appraisal
    is_assessor = models.BooleanField(default=False)
    app_categories = models.ManyToManyField(JobCategory, blank=True, related_name="userprofile_acr_categories", verbose_name="ACR Categories")
    app_institutes = models.ManyToManyField(Institute, blank=True, related_name="userprofile_app_institutes")
    app_departments = models.ManyToManyField(Department, blank=True, related_name="userprofile_app_departments")
    app_wings = models.ManyToManyField(Wing, blank=True, related_name="userprofile_app_wings", verbose_name="Wings")
    app_types = models.ManyToManyField(AppraisalType, blank=True, related_name="userprofile_app_types", verbose_name="App Types")
    app_subjects = models.ManyToManyField(Subject, blank=True, related_name="userprofile_app_subjects", verbose_name="App Subjects")

    # Inspection
    is_inspector = models.BooleanField(default=False)
    inspection_categories = models.ManyToManyField(JobCategory, blank=True, related_name="userprofile_inspection_categories", verbose_name="Inspection Categories")
    inspection_institutes = models.ManyToManyField(Institute, blank=True, related_name="userprofile_inspection_institutes", verbose_name="Inspection Institutes")
    inspection_departments = models.ManyToManyField(Department, blank=True, related_name="userprofile_inspection_departments")
    inspection_wings = models.ManyToManyField(Wing, blank=True, related_name="userprofile_inspection_wings", verbose_name="Inspection Wings")
    inspection_types = models.ManyToManyField(AppraisalType, blank=True, related_name="userprofile_inspection_types", verbose_name="Inspection Domains")
    inspection_subjects = models.ManyToManyField(Subject, blank=True, related_name="userprofile_inspection_subjects", verbose_name="Inspection Subjects")
