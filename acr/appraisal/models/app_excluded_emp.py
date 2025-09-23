from django.db import models
from django.conf import settings
from accounts.models.academicyear import AcademicYear
from accounts.models.employee import Employee  
from appraisal.models.appraisal_type import AppraisalType

class AppExcludedEmp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="excluded_emps")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="excluded_emps")
    appraisal_type = models.ForeignKey( AppraisalType,on_delete=models.CASCADE, related_name="excluded_emps")
    ex_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="excluded_records"   )
    description = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Excluded Employee"
        verbose_name_plural = "Excluded Employees"
        unique_together = ("academic_year", "appraisal_type", "ex_employee")

    def __str__(self):
        return f"{self.ex_employee} excluded for {self.appraisal_type} ({self.academic_year})"
