from django.db import models
from django.core.validators import MaxValueValidator
from requests import request
from home import choices
from accounts.models.institute import Institute, Department, Subject, Wing

class EmploymentStatus(models.Model):  # Working, Left, etc.
    name = models.CharField(max_length=20, unique=True, verbose_name="Employment Status")
    description = models.TextField(blank=True, null=True, help_text="Additional details about this status")

    def __str__(self):
        return self.name  # ✅ Corrected: Return the name directly

    class Meta:
        verbose_name = "Employment Status"
        verbose_name_plural = "Employment Statuses"

class JobCategory(models.Model): # teaching, Nonm-teaching etc
    category_code = models.CharField(max_length=2, unique=True)  # Allows flexibility in codes
    category_name = models.CharField(max_length=20, unique=True)  # Open-ended category names

    def __str__(self):
        return self.category_name

class JobPost(models.Model):  # TGT/PGT
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name="job_posts")
    post_name = models.CharField(max_length=10, default='TGT')  
    short_name = models.CharField(max_length=5, default='TGT')  
    display_name = models.CharField(max_length=15, default='Teacher')  
    description = models.CharField(max_length=50, default='Teaching Post Description')  

    def __str__(self):
        return self.display_name
    class Meta:
        unique_together = ['category', 'post_name']  # Ensures unique job post per category

class WorkingEmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(employment_status__name__iexact="Working")  # Case-insensitive match
    
class Employee(models.Model):
    emp_code = models.PositiveIntegerField(unique=True, validators=[MaxValueValidator(99999)], help_text="Enter a card number (up to 99999)", db_index=True)
    emp_name = models.CharField(max_length=30, verbose_name="Employee Name")
    job_categories = models.ManyToManyField(JobCategory, blank=True, related_name="employees")
    institutes = models.ManyToManyField(Institute, blank=True, related_name="employees")
    departments = models.ManyToManyField(Department, blank=True, related_name="employees")
    teaching_posts = models.ManyToManyField(JobPost, blank=True, related_name="employees")
    subjects = models.ManyToManyField(Subject, blank=True, related_name="employees")
    wings = models.ManyToManyField(Wing, blank=True, related_name="employees", verbose_name="Employee Wings")
    employment_status = models.ForeignKey(EmploymentStatus, on_delete=models.SET_NULL, null=True, blank=True, default=1, related_name="employees", verbose_name="Employment Status")    # Default manager (Returns all employees)
    
    objects = models.Manager()  
    # Custom managers
    working_employees = WorkingEmployeeManager()  # Returns only working employees
    
    @classmethod
    def get_employee_detail_by_code(cls, emp_code):
        """Fetch employee details using emp_code."""
        try:
            return cls.objects.get(emp_code=emp_code)
        except cls.DoesNotExist:
            return None
    def __str__(self):
        return f"{self.emp_name} ({self.emp_code})" 


 

    
    