from django.db import models
from django.db.models import Max, Sum
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.models.academicyear import AcademicYear
from accounts.models.employee import Employee, JobCategory
from accounts.models.institute import Institute
from appraisal.models.appraisal_type import AppraisalType
from appraisal.models.scale import Item


class AppraisalDataItemWise(models.Model):
    appraisal_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                       related_name="appraisals", verbose_name="Appraisal Year")
    appraisal_type = models.ForeignKey(AppraisalType, on_delete=models.CASCADE,
                                       related_name="appraisals", verbose_name="Appraisal Type")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name="appraisals", verbose_name="Employee")
    emp_institute = models.ForeignKey(Institute,  on_delete=models.CASCADE, default = 1,
                                 related_name="appraisals", verbose_name="Employee Institute")
    emp_job_category= models.ForeignKey(JobCategory,  on_delete=models.CASCADE, default = 1,
                                 related_name="appraisals", verbose_name="Employee Job Category")
    appraisal_no = models.PositiveIntegerField(verbose_name="Appraisal No", null=True, blank=True)

    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             related_name="appraisal_entries", verbose_name="Item")
    max_score = models.PositiveIntegerField(verbose_name="Maximum Score")
    obt_score = models.PositiveIntegerField(verbose_name="Obtained Score")

    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="itemwise_appraisals")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Appraisal Data"
        verbose_name_plural = "Appraisal Data"
        unique_together = ("appraisal_year", "appraisal_type", "employee", "appraisal_no", "item")
        ordering = ["appraisal_year", "appraisal_type", "employee", "appraisal_no", "item"]

    def __str__(self):
        return f"{self.employee} - {self.appraisal_type} ({self.appraisal_year}) No.{self.appraisal_no}"

    def clean(self):
        if self.obt_score > self.max_score:
            raise ValidationError("Obtained score cannot be greater than maximum score.")

    def save(self, *args, **kwargs):
        if not self.pk and (self.appraisal_no is None or self.appraisal_no == 0):
            last_no = AppraisalDataItemWise.objects.filter(
                appraisal_year=self.appraisal_year,
                appraisal_type=self.appraisal_type,
                employee=self.employee
            ).aggregate(Max("appraisal_no"))["appraisal_no__max"] or 0
            self.appraisal_no = last_no + 1
        super().save(*args, **kwargs)


class TotalAppraisalData(models.Model):
    appraisal_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                       related_name="total_appraisals")
    appraisal_type = models.ForeignKey(AppraisalType, on_delete=models.CASCADE,
                                       related_name="total_appraisals")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name="total_appraisals")
    emp_institute = models.ForeignKey(Institute,  on_delete=models.CASCADE, default = 1,
                                 related_name="total_appraisals", verbose_name="Employee Institute")
    emp_job_category= models.ForeignKey(JobCategory,  on_delete=models.CASCADE, default = 1,
                                 related_name="ttal_appraisals", verbose_name="Employee Job Category")
    appraisal_no = models.PositiveIntegerField(editable=False, null = True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="total_appraisals")
    max_score = models.FloatField(default=0)
    obt_score = models.FloatField(default=0)
    remarks = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Total Appraisal Data"
        verbose_name_plural = "Total Appraisal Data"
        unique_together = ("appraisal_year", "appraisal_type", "employee", "appraisal_no")
        ordering = ["employee", "appraisal_year", "appraisal_type", "appraisal_no"]



    def __str__(self):
        return f"{getattr(self.employee, 'emp_name', self.employee)} - {getattr(self.appraisal_type, 'display_name', self.appraisal_type)} ({self.appraisal_year}) [#{self.appraisal_no}]"

